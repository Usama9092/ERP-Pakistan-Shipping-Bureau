"""EPAS production Supabase client with Streamlit-session isolation.

Never cache an authenticated Supabase client globally. Each Streamlit session
owns its own client and therefore its own mutable auth session/JWT state.
"""
from __future__ import annotations
import os
from pathlib import Path
import streamlit as st

try:
    from supabase import create_client, Client  # type: ignore
    _SUPABASE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SUPABASE_SDK_AVAILABLE = False
    Client = None  # type: ignore


def _read_secret(key: str) -> str | None:
    try:
        return st.secrets[key]  # type: ignore[index]
    except Exception:
        return os.getenv(key)


def _load_demo_env_file() -> None:
    """Load the bundled demo environment when no explicit runtime mode is set.

    This makes the public 8501 demo work even when the user starts Streamlit
    directly with `streamlit run app.py` instead of the helper script. The
    production promotion script removes `.env.demo`, so a production package
    cannot silently fall back to demo mode. Explicit environment variables
    always take precedence.
    """
    explicit_mode = os.getenv("EPAS_RUNTIME_MODE")
    explicit_demo_flag = os.getenv("EPAS_ENABLE_DEMO_MODE")
    if explicit_mode or explicit_demo_flag in ("1", "demo", "DEMO", "Demo"):
        return
    env_file = Path(__file__).resolve().parents[1] / ".env.demo"
    if not env_file.exists():
        return
    try:
        for raw in env_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('\"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError:
        # Demo auto-loading is a convenience only. If the file cannot be read,
        # normal production fail-closed behavior remains in effect.
        return


def runtime_mode() -> str:
    """Return the runtime mode: demo or production."""
    _load_demo_env_file()
    mode = os.getenv("EPAS_RUNTIME_MODE", os.getenv("EPAS_ENABLE_DEMO_MODE", "0"))
    if mode in ("1", "demo", "DEMO", "Demo"):
        return "demo"
    return "production"


def is_demo_mode() -> bool:
    return runtime_mode() == "demo"


def get_client() -> "Client":
    """Return a Supabase client isolated to the current Streamlit session."""
    if is_demo_mode():
        raise RuntimeError("The demo runtime does not use a live Supabase client. Use the demo authentication/query adapter.")
    if not _SUPABASE_SDK_AVAILABLE:
        raise RuntimeError("Supabase SDK is not installed. Install requirements.txt before starting EPAS.")
    url = _read_secret("SUPABASE_URL")
    key = _read_secret("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("EPAS production configuration is incomplete: SUPABASE_URL and SUPABASE_ANON_KEY are required.")

    client = st.session_state.get("epas_supabase_client_v35")
    if client is not None:
        return client

    client = create_client(url, key)
    st.session_state["epas_supabase_client_v35"] = client
    return client


def connection_badge() -> tuple[str, str]:
    if is_demo_mode():
        return "Demo mode · in-memory sample data", "conn-pill conn-pill--demo"
    try:
        get_client()
        return "Supabase connected", "conn-pill conn-pill--live"
    except Exception:
        return "Production configuration required", "conn-pill conn-pill--demo"
