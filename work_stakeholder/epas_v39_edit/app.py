"""EPAS v4.1.4 production Streamlit entrypoint — GM stakeholder registry + project selector.
Historical modules remain archived for cumulative migration/testing coverage; the active surface is v4.1.3.
The page is deliberately role-native and view-gated so a rerun renders only one operational surface at a time.
"""

from __future__ import annotations

# Bootstrap the application root so direct Streamlit launches work regardless
# of the caller's current working directory (e.g. GitHub Codespaces).
# This must run before importing the local ``config`` package.
import sys
from pathlib import Path
_APP_ROOT = Path(__file__).resolve().parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

import streamlit as st
from config import settings as cfg
from styles.theme import inject_css
from components.auth_gate import render as render_auth
from components.branding import render_topbar
from components.gm_production import render as render_gm
from components.dm_production import render as render_dm
from components.role_workspaces import render_engineer, render_surveyor, render_designer, render_ship_management, render_readonly_stakeholder
from components.professional_center_v36 import render as render_professional_center
from components.role_cockpits_v40 import render as render_role_cockpit
from components.project_workspace_v40 import render as render_project_workspace, render_project_launcher
from components.survey_lifecycle_v36 import render as render_survey_lifecycle_v36, render_role_acceptance as render_v36_acceptance
render_v33_acceptance = render_v36_acceptance  # archived compatibility alias



st.set_page_config(page_title=f"{cfg.APP_NAME} · v4.1.4", page_icon="🚢", layout="wide", initial_sidebar_state="expanded")
inject_css()
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stAppViewContainer"] { overflow: hidden; }
    [data-testid="stSidebarCollapsedControl"],
    button[title="Hide sidebar"],
    button[title="Show sidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 70px !important;
        left: 0 !important;
        width: 240px !important;
        max-width: 240px !important;
        height: calc(100vh - 70px) !important;
        z-index: 9999 !important;
        transform: none !important;
        transition: none !important;
    }
    [data-testid="stMainBlockContainer"], .main .block-container {
        padding-top: 95px !important;
        padding-left: 2rem !important;
        padding-right: 1rem !important;
        margin-left: 240px !important;
        width: calc(100vw - 240px) !important;
        max-width: calc(100vw - 240px) !important;
    }
    .psb-topbar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 70px !important;
        z-index: 99999 !important;
        background: #0b2530 !important;
        border-radius: 0 !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.12) !important;
        margin: 0 !important;
        padding: 12px 1.5rem !important;
        border: none !important;
    }
    .psb-context-row {
        position: fixed !important;
        top: 70px !important;
        left: 0 !important;
        width: 100vw !important;
        height: 26px !important;
        z-index: 99998 !important;
        background: #0b2530 !important;
        color: #e9f1f4 !important;
        margin: 0 !important;
        padding: 0 1.5rem !important;
        border-top: 1px solid rgba(255,255,255,0.08) !important;
        border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    .psb-topbar__org,
    .psb-topbar__product,
    .psb-role-pill,
    .psb-user-block strong,
    .psb-user-block span,
    .psb-context-label,
    .psb-context-value,
    .psb-secure-badge {
        color: #f3f9fb !important;
    }
    .psb-role-pill {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }
    .psb-topbar__brand,
    .psb-topbar__context {
        z-index: 2;
    }
    @media (max-width: 900px) {
        [data-testid="stSidebar"] { width: 220px !important; max-width: 220px !important; }
        [data-testid="stMainBlockContainer"], .main .block-container {
            margin-left: 220px !important;
            width: calc(100vw - 220px) !important;
            max-width: calc(100vw - 220px) !important;
            padding-left: 1rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

user = render_auth()
if not user:
    st.stop()

role = user.get('role')

NAV = {
    'gm': [('Projects', 'projects')],
    'dm': [('Projects', 'projects')],
    'engineer': [('Projects', 'projects')],
    'surveyor': [('Projects', 'projects')],
    'designer': [('Projects', 'projects')],
    'ship_management': [('Projects', 'projects')],
    'owner': [('Projects', 'projects')],
    'shipyard': [('Projects', 'projects')],
}

if role not in NAV:
    st.error("Your account has no valid EPAS workflow role. Contact the system administrator.")
    st.stop()

options = NAV[role]
state_key = f"epas_view_{role}_v414"
labels = [x[0] for x in options]
view_titles = {label: key for label, key in options}

# Fixed global navigation before project selection.
project_id = st.session_state.get("selected_project_id")
if not project_id:
    with st.sidebar:
        st.markdown('<div class="psb-global-nav-label">GLOBAL NAVIGATION</div>', unsafe_allow_html=True)
        selected_label = st.radio(
            "WORKSPACE",
            labels,
            index=0,
            key=state_key,
            label_visibility="collapsed",
        )
        view = view_titles[selected_label]
        st.markdown('<div class="psb-sidebar-divider"></div>', unsafe_allow_html=True)
        if st.button("Sign out", key="global_signout_v413", use_container_width=True):
            from config.production_auth import sign_out
            sign_out()
            st.rerun()
else:
    view = "project_context"

# PSB application shell: authenticated identity, current workspace and secure status.
render_topbar(user, "Project Workspace" if project_id else selected_label)

if project_id:
    # Once a project is opened, it becomes the primary context. The role-specific
    # project navigation sits on the left and all project operations remain in the
    # selected project boundary.
    render_project_workspace(role, project_id)
    st.stop()

# Always render the lightweight role header/cockpit; all heavy pages are mutually exclusive.
render_role_cockpit(role)

if view == 'cockpit':
    st.markdown("### Next-action guidance")
    st.caption("Select an operational surface above. Only the selected page is loaded, reducing unnecessary database calls on Streamlit reruns.")
elif view == 'projects':
    render_project_launcher(role)
elif view == 'operations':
    if role == cfg.ROLE_GM:
        render_gm()
    elif role == cfg.ROLE_DM:
        render_dm()
    elif role == cfg.ROLE_ENGINEER:
        render_engineer()
    elif role == cfg.ROLE_SURVEYOR:
        render_surveyor()
    elif role == cfg.ROLE_DESIGNER:
        render_designer()
    elif role == cfg.ROLE_SHIP_MANAGEMENT:
        render_ship_management()
    elif role in (cfg.ROLE_OWNER, cfg.ROLE_SHIPYARD):
        render_readonly_stakeholder()
elif view == 'survey':
    render_professional_center(include_security=(role in (cfg.ROLE_GM, cfg.ROLE_DM)))
    render_survey_lifecycle_v36()
elif view == 'governance':
    render_professional_center(include_security=True)
    render_v36_acceptance()
