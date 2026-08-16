"""Reusable Streamlit UX/security helpers for v3.0."""
from __future__ import annotations
import hashlib
import streamlit as st


def error_reference(context: str, exc: Exception) -> str:
    fingerprint = hashlib.sha256(f"{context}:{type(exc).__name__}:{exc}".encode('utf-8')).hexdigest()[:10].upper()
    return f"EPAS-{fingerprint}"


def show_safe_error(context: str, exc: Exception) -> None:
    ref = error_reference(context, exc)
    st.error(f"{context} could not be completed. Reference {ref}.")
    with st.expander('Technical detail', expanded=False):
        st.caption(f"{type(exc).__name__}: {exc}")
