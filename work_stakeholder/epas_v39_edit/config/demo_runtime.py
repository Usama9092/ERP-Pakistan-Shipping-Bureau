"""EPAS public/demo runtime for GitHub Codespaces / port 8501 previews.

Demo mode is deliberately isolated from production authentication and uses the
existing realistic seed dataset. It is enabled only when EPAS_RUNTIME_MODE=demo.
Production mode is fail-closed and requires Supabase credentials.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import os
import streamlit as st
from database.seed_data import build_seed_db

DEMO_PASSWORD = os.getenv("EPAS_DEMO_PASSWORD", "PSB-Demo-2026!")
DEMO_USERS = {
    "gm@classification.com": {"full_name": "Ahmed Al-Maktoum", "role": "gm"},
    "m.hassan@classification.com": {"full_name": "Muhammad Hassan", "role": "dm"},
    "r.alfarsi@classification.com": {"full_name": "Rania Al-Farsi", "role": "dm"},
    "faruk@classification.com": {"full_name": "Mehmet Faruk", "role": "engineer"},
    "park@classification.com": {"full_name": "Capt. Park Min-jae", "role": "surveyor"},
    "designer@damen.com": {"full_name": "Tayyab Qureshi", "role": "designer"},
    "shipyard@damen.com": {"full_name": "Mohammed Ali", "role": "shipyard"},
    "shipmanagement@oceanic.co": {"full_name": "John Smith", "role": "ship_management"},
    "owner@vesselholdings.com": {"full_name": "Fatima Noor", "role": "owner"},
}


def _db() -> dict:
    db = st.session_state.get("epas_demo_db_v40")
    if db is None:
        db = build_seed_db()
        st.session_state["epas_demo_db_v40"] = db
    return db


def reset_demo() -> None:
    st.session_state["epas_demo_db_v40"] = build_seed_db()


def current_user() -> dict | None:
    email = st.session_state.get("epas_demo_user_email")
    if not email or email not in DEMO_USERS:
        return None
    base = next((p for p in _db()["profiles"] if p.get("email") == email), None)
    return base.copy() if base else {"id": email, "email": email, **DEMO_USERS[email]}


def sign_in(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if email not in DEMO_USERS or password != DEMO_PASSWORD:
        return False, "Demo sign-in failed. Use one of the published demo emails and the demo password."
    st.session_state["epas_demo_user_email"] = email
    st.session_state["epas_last_activity"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    return True, ""


def sign_out() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("epas_demo_") or key in {"selected_project_id", "project_nav_key"}:
            st.session_state.pop(key, None)


def request_password_reset(email: str) -> tuple[bool, str]:
    return True, "Demo mode does not send email. In production, password reset is handled by Supabase Auth."


def table(name: str) -> list[dict]:
    return list(_db().get(name, []))
