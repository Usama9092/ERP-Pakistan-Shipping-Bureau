"""Optional server-side malware scanning hook for controlled document ingestion."""
from __future__ import annotations
import os, shutil, subprocess
from typing import Tuple


def scan_bytes(data: bytes) -> Tuple[bool, str]:
    """Scan bytes with ClamAV when configured/required.

    EPAS_REQUIRE_ANTIVIRUS=1 makes the application fail closed if ClamAV is not
    available. In development/test environments the default is permissive.
    """
    require = os.getenv("EPAS_REQUIRE_ANTIVIRUS", "0") == "1"
    engine = os.getenv("EPAS_CLAMSCAN_BIN", "clamscan")
    binary = shutil.which(engine)
    if not binary:
        if require:
            return False, "Server-side malware scanner is required but ClamAV is not installed."
        return True, "Malware scan skipped: scanner not configured."
    try:
        proc = subprocess.run(
            [binary, "--stdout", "--no-summary", "--infected", "-"],
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=int(os.getenv("EPAS_ANTIVIRUS_TIMEOUT_SECONDS", "60")),
            check=False,
        )
    except Exception as exc:
        return (False, f"Malware scan failed: {exc}") if require else (True, f"Malware scan unavailable: {exc}")
    if proc.returncode == 0:
        return True, "Malware scan passed."
    if proc.returncode == 1:
        return False, "Malware scanner detected a threat."
    return (False, "Malware scanner returned an error.") if require else (True, "Malware scanner returned an error; upload policy is permissive.")
