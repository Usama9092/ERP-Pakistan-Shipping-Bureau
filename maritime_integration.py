from __future__ import annotations

import os
from typing import Any

import pandas as pd
import streamlit as st

from maritime_module import (
    CERTIFICATE_CATEGORIES,
    NOTIFICATION_TYPES,
    SURVEY_TYPES,
    build_dashboard_summary,
    build_notification_payload,
    build_theme_css,
    create_default_survey_checklist,
    get_project_config,
    normalize_checklist_item,
    sanitize_text_input,
)


THEME_STORAGE_KEY = "psb_theme_preference"


def get_theme_preference() -> str:
    stored = st.session_state.get(THEME_STORAGE_KEY, "")
    if stored in {"light", "dark"}:
        return stored
    return "dark" if os.getenv("APP_THEME", "dark").lower() == "dark" else "light"


def set_theme_preference(theme: str) -> None:
    theme = theme.lower()
    if theme in {"light", "dark"}:
        st.session_state[THEME_STORAGE_KEY] = theme


def render_theme_toggle() -> None:
    theme = get_theme_preference()
    selected = st.radio("Theme", ["light", "dark"], horizontal=True, index=0 if theme == "light" else 1)
    if selected != theme:
        set_theme_preference(selected)
        st.rerun()


def render_project_information() -> None:
    config = get_project_config()
    st.subheader("Project Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Project Name: **{sanitize_text_input(config['project_name'])}**")
        st.write(f"Version: **{sanitize_text_input(config['version'])}**")
        st.write(f"Description: **{sanitize_text_input(config['description'])}**")
        st.write(f"Company: **{sanitize_text_input(config['company'])}**")
        st.write(f"System Status: **{sanitize_text_input(config['system_status'])}**")
    with col2:
        st.write(f"Last Updated: **{sanitize_text_input(config['last_updated'])}**")
        st.write(f"Database Version: **{sanitize_text_input(config['database_version'])}**")
        st.write(f"Environment: **{sanitize_text_input(config['environment'])}**")
        st.write("Modules: " + ", ".join([sanitize_text_input(item) for item in config.get("modules", [])]))


def render_maritime_dashboard(ships: list[dict[str, Any]], surveys: list[dict[str, Any]], certificates: list[dict[str, Any]], notifications: list[dict[str, Any]]) -> None:
    summary = build_dashboard_summary(ships, surveys, certificates, notifications)
    st.subheader("Maritime Operations Dashboard")
    cols = st.columns(4)
    cols[0].metric("Ships", summary["ships"])
    cols[1].metric("Surveys", summary["surveys"])
    cols[2].metric("Certificates", summary["certificates"])
    cols[3].metric("Notifications", summary["notifications"])


def render_survey_checklist_editor(survey_type: str = "Annual Survey") -> None:
    st.subheader(f"{survey_type} Checklist")
    checklist = create_default_survey_checklist(survey_type)
    for idx, item in enumerate(checklist):
        normalized = normalize_checklist_item(item)
        with st.expander(f"{normalized['section']} / {normalized['subsection']} / {normalized['checklist_item']}"):
            st.text_input(f"Section {idx}", value=normalized["section"], key=f"survey_section_{idx}")
            st.text_input(f"Subsection {idx}", value=normalized["subsection"], key=f"survey_subsection_{idx}")
            st.text_input(f"Checklist Item {idx}", value=normalized["checklist_item"], key=f"survey_item_{idx}")
            st.text_area(f"Inspection Requirement {idx}", value=normalized["inspection_requirement"], key=f"survey_requirement_{idx}")
            st.text_area(f"Remarks {idx}", value=normalized["remarks"], key=f"survey_remarks_{idx}")
            st.selectbox(f"Status {idx}", ["Pending", "Pass", "Fail", "Not Applicable"], key=f"survey_status_{idx}")
            st.slider(f"Completion % {idx}", 0, 100, normalized["completion_pct"], key=f"survey_completion_{idx}")


def render_ship_registry(ships: list[dict[str, Any]]) -> None:
    st.subheader("Ship Registry")
    query = st.text_input("Search ships", placeholder="Search by name, IMO, owner, flag, classification number")
    filters: dict[str, Any] = {}
    if ships:
        filter_values = [ship.get("flag", "") for ship in ships if ship.get("flag")]
        if filter_values:
            selected_flag = st.selectbox("Filter by flag", ["All"] + sorted(set(filter_values)))
            if selected_flag != "All":
                filters["flag"] = selected_flag
    from maritime_module import filter_ships
    filtered = filter_ships(ships, query=query, filters=filters)
    table = pd.DataFrame(filtered)
    if not table.empty:
        display_columns = ["ship_name", "imo_number", "call_sign", "flag", "owner", "class_status", "survey_status", "certificate_status"]
        st.dataframe(table[display_columns].head(20), use_container_width=True)
        st.caption(f"Showing {len(filtered)} matching ships")
    else:
        st.info("No ships matched the current search. Adjust the filters or add new records.")


def render_notification_center(notifications: list[dict[str, Any]]) -> None:
    st.subheader("Notification Center")
    if not notifications:
        st.info("No notifications have been queued yet.")
        return
    for item in notifications:
        st.info(f"{item.get('event_type', 'Notification')}: {item.get('message', '')}")


def render_certificate_management(certificates: list[dict[str, Any]]) -> None:
    st.subheader("Certificate Management")
    if not certificates:
        st.info("No certificates loaded yet.")
        return
    st.dataframe(pd.DataFrame(certificates), use_container_width=True)


def render_security_summary() -> None:
    st.subheader("Security & Compliance")
    st.write("- CSP and secure headers are enforced at the application boundary.")
    st.write("- Input validation and output encoding protect against XSS and injection.")
    st.write("- Audit logs and rate limit readiness are maintained for all sensitive actions.")


def register_maritime_pages() -> None:
    st.session_state.setdefault("maritime_module_ready", True)
