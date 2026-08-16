"""Centralized controlled-file validation for EPAS v3.0.
Validates extension, magic bytes, MIME, size and produces a real SHA-256 of file bytes.
"""
from __future__ import annotations
import hashlib
from typing import Any
from dataclasses import dataclass

MAX_PDF_BYTES = 50 * 1024 * 1024
MAX_IMAGE_BYTES = 25 * 1024 * 1024

_SIGNATURES = {
    'pdf': (b'%PDF-', {'application/pdf', 'application/octet-stream'}),
    'jpg': (b'\xff\xd8\xff', {'image/jpeg', 'image/jpg', 'application/octet-stream'}),
    'jpeg': (b'\xff\xd8\xff', {'image/jpeg', 'image/jpg', 'application/octet-stream'}),
    'png': (b'\x89PNG\r\n\x1a\n', {'image/png', 'application/octet-stream'}),
}


@dataclass(frozen=True)
class ValidatedUpload:
    content: bytes
    file_name: str
    mime_type: str
    size_bytes: int
    sha256: str


def materialize_upload(uploaded: Any, allowed: set[str], max_bytes: int) -> ValidatedUpload:
    """Read an UploadedFile exactly once, validate it, and return one byte buffer."""
    if uploaded is None:
        raise ValueError("A file is required.")
    name = str(getattr(uploaded, 'name', '') or '').replace('\\', '_').replace('/', '_')
    mime = str(getattr(uploaded, 'type', '') or '').lower() or 'application/octet-stream'
    declared_size = getattr(uploaded, 'size', None)
    if declared_size is not None:
        try:
            if int(declared_size) > max_bytes:
                raise ValueError(f"File exceeds the {max_bytes // (1024*1024)} MB limit.")
        except (TypeError, ValueError) as exc:
            if isinstance(exc, ValueError) and 'exceeds' in str(exc):
                raise
    try:
        raw = uploaded.getbuffer()
        content = raw.tobytes()
    except Exception:
        content = uploaded.getvalue()
    if not content:
        raise ValueError('The uploaded file is empty.')
    size_bytes=len(content)
    if size_bytes > max_bytes:
        raise ValueError(f'File exceeds the {max_bytes // (1024*1024)} MB limit.')
    suffix = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if suffix not in allowed:
        raise ValueError(f'File type .{suffix or "unknown"} is not permitted.')
    sig = _SIGNATURES.get(suffix)
    if sig is None:
        raise ValueError(f'No controlled signature rule exists for .{suffix}.')
    expected_sig, allowed_mimes = sig
    if not content.startswith(expected_sig):
        raise ValueError('The uploaded file signature does not match its declared file type.')
    if mime and mime not in allowed_mimes:
        raise ValueError('The declared MIME type does not match the detected file signature.')
    if suffix == 'pdf' and b'/JavaScript' in content[:2_000_000]:
        raise ValueError('PDF content contains a JavaScript marker and requires security review.')
    return ValidatedUpload(content, name, mime, size_bytes, hashlib.sha256(content).hexdigest())



def validate_upload_descriptor(uploaded: Any, allowed: set[str], max_bytes: int) -> tuple[bool, str]:
    """Cheap UI-side check that uses UploadedFile metadata only; does not read file bytes."""
    if uploaded is None:
        return False, 'A file is required.'
    name = str(getattr(uploaded, 'name', '') or '')
    declared_size = getattr(uploaded, 'size', None)
    if declared_size is not None and int(declared_size) > max_bytes:
        return False, f'File exceeds the {max_bytes // (1024*1024)} MB limit.'
    suffix = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if suffix not in allowed:
        return False, f'File type .{suffix or "unknown"} is not permitted.'
    return True, ''

def file_sha256(data: bytes) -> str:
    """Return the SHA-256 of the actual uploaded bytes."""
    if not data:
        raise ValueError('Cannot hash an empty file')
    return hashlib.sha256(data).hexdigest()


def validate_uploaded_file(uploaded: Any, allowed: set[str], max_bytes: int) -> tuple[bool, str]:
    try:
        materialize_upload(uploaded, allowed, max_bytes)
        return True, ''
    except ValueError as exc:
        return False, str(exc)


def validated_upload_metadata(uploaded: Any) -> dict[str, Any]:
    """Return immutable metadata for a validated upload."""
    v = materialize_upload(uploaded, {'pdf','jpg','jpeg','png'}, max(MAX_PDF_BYTES, MAX_IMAGE_BYTES))
    return {
        'file_name': v.file_name,
        'mime_type': v.mime_type,
        'size_bytes': v.size_bytes,
        'sha256': v.sha256,
    }
