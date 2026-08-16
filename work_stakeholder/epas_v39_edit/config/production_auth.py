"""Production Supabase authentication for EPAS v3.0."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import streamlit as st
import os
from config.supabase_client import get_client, is_demo_mode

SESSION_TIMEOUT_MINUTES = max(5, int(os.environ.get("EPAS_SESSION_TIMEOUT_MINUTES", "30")))


def current_user() -> dict | None:
    if is_demo_mode():
        from config import demo_runtime
        return demo_runtime.current_user()
    client = get_client()
    try:
        auth_user = client.auth.get_user().user
    except Exception:
        return None
    if not auth_user:
        return None
    last = st.session_state.get('epas_last_activity')
    now = datetime.now(timezone.utc)
    if last:
        try:
            if now - last > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                client.auth.sign_out()
                st.session_state.clear()
                return None
        except Exception:
            st.session_state.pop('epas_last_activity', None)
    st.session_state['epas_last_activity'] = now
    if __import__('os').getenv('EPAS_REQUIRE_MFA','0') == '1':
        try:
            session = client.auth.get_session().session
            aal = getattr(session, 'aal', None)
            if aal != 'aal2':
                st.warning('Multi-factor authentication is required for this deployment. Complete MFA and sign in again.')
                client.auth.sign_out()
                return None
        except Exception:
            st.warning('MFA status could not be verified. Access is blocked by policy.')
            client.auth.sign_out()
            return None
    rows = client.table('profiles').select('*').eq('id', auth_user.id).limit(1).execute().data
    if not rows:
        return None
    return rows[0]


def sign_in(email: str, password: str) -> tuple[bool, str]:
    if is_demo_mode():
        from config import demo_runtime
        return demo_runtime.sign_in(email, password)
    client = get_client()
    try:
        client.auth.sign_in_with_password({'email': email.strip(), 'password': password})
        user = current_user()
        if not user:
            client.auth.sign_out()
            return False, 'Authenticated user has no EPAS profile. Ask the administrator to create the profile.'
        try:
            client.rpc('epas_record_security_event_v29', {'p_event_type':'LOGIN_SUCCESS','p_success':True,'p_details':{'email_domain': email.split('@')[-1] if '@' in email else ''}}).execute()
        except Exception:
            pass
        return True, ''
    except Exception as exc:
        try:
            client.rpc('epas_record_security_event_v29', {'p_event_type':'LOGIN_FAILURE','p_success':False,'p_details':{}}).execute()
        except Exception:
            pass
        return False, 'Sign-in failed. Verify your credentials or contact the administrator.'


def request_password_reset(email: str) -> tuple[bool, str]:
    if is_demo_mode():
        from config import demo_runtime
        return demo_runtime.request_password_reset(email)
    try:
        get_client().auth.reset_password_email(email.strip())
        return True, 'If the account exists, a password-reset message has been requested.'
    except Exception:
        return False, 'Password reset could not be requested. Contact the administrator if the issue persists.'


def sign_out() -> None:
    if is_demo_mode():
        from config import demo_runtime
        demo_runtime.sign_out()
        return
    try:
        get_client().auth.sign_out()
    finally:
        for key in ['selected_project_id','selected_drawing_id','selected_rfi_id','epas_last_activity','epas_supabase_client_v35','epas_read_cache_v31']:
            st.session_state.pop(key, None)


def require_role(allowed: set[str]) -> dict | None:
    user = current_user()
    if not user:
        return None
    if user.get('role') not in allowed:
        st.error(f'This account is not authorized for this workspace. Required role: {", ".join(sorted(allowed))}.')
        st.stop()
    return user
