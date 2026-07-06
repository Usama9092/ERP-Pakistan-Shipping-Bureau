from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import time
from typing import Any


class PasswordSecurity:
    """Strong password hashing and policy enforcement."""

    def __init__(self, iterations: int = 120_000) -> None:
        self.iterations = iterations

    def hash_password(self, password: str) -> str:
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string")
        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iterations)
        return f"pbkdf2_sha256$${self.iterations}$${salt.hex()}$${derived.hex()}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        if not isinstance(password, str) or not password:
            return False
        if not password_hash or not isinstance(password_hash, str):
            return False
        if password_hash.startswith("pbkdf2_sha256$$"):
            try:
                _, iterations, salt_hex, derived_hex = password_hash.split("$$")
                iterations = int(iterations)
                salt = bytes.fromhex(salt_hex)
                derived = bytes.fromhex(derived_hex)
                candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
                return hmac.compare_digest(candidate, derived)
            except (ValueError, TypeError):
                return False
        if re.fullmatch(r"[0-9a-f]{64}", password_hash):
            return hashlib.sha256(password.encode("utf-8")).hexdigest() == password_hash
        return False

    def is_password_strong(self, password: str) -> bool:
        if not isinstance(password, str) or len(password) < 12:
            return False
        has_upper = any(ch.isupper() for ch in password)
        has_lower = any(ch.islower() for ch in password)
        has_digit = any(ch.isdigit() for ch in password)
        has_symbol = any(not ch.isalnum() for ch in password)
        return has_upper and has_lower and has_digit and has_symbol

    def is_legacy_hash(self, password_hash: str) -> bool:
        return bool(re.fullmatch(r"[0-9a-f]{64}", password_hash))


class SessionSecurity:
    """Lightweight signed session tokens to guard against tampering."""

    def __init__(self, secret: str | None = None, timeout_minutes: int = 30) -> None:
        self.secret = secret or os.getenv("APP_SECRET_KEY", "change-me-in-production")
        self.timeout_seconds = max(60, timeout_minutes * 60)

    def issue_session_token(self, user_id: str, role: str, state: dict[str, Any]) -> str:
        payload = f"{user_id}|{role}|{int(time.time()) + self.timeout_seconds}"
        signature = hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        token = f"{payload}|{signature}"
        state["auth_session_token"] = token
        state["auth_expires_at"] = int(time.time()) + self.timeout_seconds
        state["auth_user_id"] = user_id
        state["auth_user_role"] = role
        return token

    def validate_session_token(self, state: dict[str, Any]) -> bool:
        token = state.get("auth_session_token")
        expires_at = int(state.get("auth_expires_at", 0))
        if not token or not isinstance(token, str):
            return False
        if expires_at <= int(time.time()):
            return False
        payload, signature = token.rsplit("|", 1)
        expected = hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return False
        return True

    def clear_session(self, state: dict[str, Any]) -> None:
        for key in ["auth_session_token", "auth_expires_at", "auth_user_id", "auth_user_role"]:
            state.pop(key, None)


class LoginAttemptGuard:
    """Track repeated login failures and temporarily lock accounts."""

    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15) -> None:
        self.max_attempts = max_attempts
        self.lockout_seconds = max(60, lockout_minutes * 60)

    def _guard_state(self, state: dict[str, Any]) -> dict[str, Any]:
        if "_auth_guard" not in state:
            state["_auth_guard"] = {}
        return state["_auth_guard"]

    def _key(self, login_key: str) -> str:
        return login_key.lower().strip()

    def is_locked(self, login_key: str, state: dict[str, Any]) -> bool:
        guard = self._guard_state(state)
        key = self._key(login_key)
        entry = guard.get(key, {})
        if not entry:
            return False
        if entry.get("count", 0) < self.max_attempts:
            return False
        elapsed = time.time() - float(entry.get("locked_at", 0))
        if elapsed >= self.lockout_seconds:
            guard.pop(key, None)
            return False
        return True

    def record_failure(self, login_key: str, state: dict[str, Any]) -> None:
        guard = self._guard_state(state)
        key = self._key(login_key)
        entry = guard.get(key, {"count": 0})
        entry["count"] = int(entry.get("count", 0)) + 1
        if entry["count"] >= self.max_attempts:
            entry["locked_at"] = time.time()
        guard[key] = entry

    def record_success(self, login_key: str, state: dict[str, Any]) -> None:
        guard = self._guard_state(state)
        guard.pop(self._key(login_key), None)

    def remaining_seconds(self, login_key: str, state: dict[str, Any]) -> int:
        guard = self._guard_state(state)
        key = self._key(login_key)
        entry = guard.get(key, {})
        if not entry or entry.get("count", 0) < self.max_attempts:
            return 0
        elapsed = time.time() - float(entry.get("locked_at", 0))
        return max(0, int(self.lockout_seconds - elapsed))
