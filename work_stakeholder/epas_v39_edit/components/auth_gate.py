"""Fail-closed PSB login gate for production EPAS v3.6.1."""
from __future__ import annotations
import streamlit as st

from config.production_auth import current_user, sign_in, request_password_reset
from config.supabase_client import is_demo_mode
from components.branding import render_login_hero


def render() -> dict | None:
    try:
        user = current_user()
    except Exception:
        st.error(
            "Pakistan Shipping Bureau production configuration is unavailable. "
            "Configure Supabase before starting the application."
        )
        st.stop()
        return None

    if user:
        return user

    left, right = st.columns([1.08, 0.92], gap="large")
    with left:
        render_login_hero()

    with right:
        st.markdown('<div class="psb-login-panel">', unsafe_allow_html=True)
        st.markdown('<div class="psb-login-panel__title">Welcome back</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="psb-login-panel__copy">'
            'Sign in with your authenticated Pakistan Shipping Bureau account to continue.'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.form("psb_login"):
            email = st.text_input("Demo email" if is_demo_mode() else "Work email", placeholder="gm@classification.com" if is_demo_mode() else "name@psb.gov.pk")
            password = st.text_input("Demo password" if is_demo_mode() else "Password", type="password", placeholder="PSB-Demo-2026!" if is_demo_mode() else "Enter your password")
            remember = st.checkbox("Remember this session", value=True)
            submitted = st.form_submit_button("Sign in to PSB →", type="primary", use_container_width=True)

        if submitted:
            ok, message = sign_in(email, password)
            if ok:
                st.rerun()
            st.error(message)

        col1, col2 = st.columns(2)
        with col1:
            st.caption("🔒 Secure access")
        with col2:
            st.caption("✓ Audit enabled")

        if is_demo_mode():
            with st.expander("📋 Demo Access Mode", expanded=False):
                st.markdown("**Demo Credentials:**")
                st.code("Email: gm@classification.com\nPassword: PSB-Demo-2026!", language="text")
                st.caption("💡 Use any published demo email from DEMO_CREDENTIALS.md with the same password.")

        with st.expander("❓ Need help? Forgot password?", expanded=False):
            reset_email = st.text_input("Account email", key="reset_email", placeholder="your.email@psb.gov.pk")
            if st.button("Request password reset", key="reset_password", use_container_width=True):
                if not reset_email.strip():
                    st.error("Enter your account email.")
                else:
                    ok, msg = request_password_reset(reset_email)
                    (st.success if ok else st.error)(msg)

        st.divider()
        st.markdown(
            '<div class="psb-login-help">Access is restricted to authorized PSB users and registered external stakeholders. '
            'Contact the system administrator if your account or role is incorrect.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="psb-login-bottom">Pakistan Shipping Bureau · Classification, Survey & Maritime Safety Management System</div>',
        unsafe_allow_html=True,
    )
    return None
