"""EPAS v4.1.4 production Streamlit entrypoint — GM stakeholder registry + project selector.
Historical modules remain archived for cumulative migration/testing coverage; the active surface is v4.1.3.
The page is deliberately role-native and view-gated so a rerun renders only one operational surface at a time.
"""

from __future__ import annotations

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
render_v33_acceptance = render_v36_acceptance

st.set_page_config(page_title=f"{cfg.APP_NAME} · v4.1.4", page_icon="🚢", layout="wide", initial_sidebar_state="expanded")
inject_css()

user = render_auth()
if not user:
    st.stop()

role = user.get('role')

NAV = {
    'gm': [('Command Center', 'cockpit'), ('Projects', 'projects'), ('Project & Plan', 'operations'), ('Survey Control', 'survey'), ('Governance & Acceptance', 'governance')],
    'dm': [('Operations Center', 'cockpit'), ('Projects', 'projects'), ('Plan / Allocation', 'operations'), ('Survey Control', 'survey'), ('Acceptance', 'governance')],
    'engineer': [('Technical Cockpit', 'cockpit'), ('Projects', 'projects'), ('Plan Appraisal', 'operations')],
    'surveyor': [('Field Cockpit', 'cockpit'), ('Projects', 'projects'), ('Survey Lifecycle', 'survey')],
    'designer': [('Submission Cockpit', 'cockpit'), ('Projects', 'projects'), ('Plan Appraisal', 'operations')],
    'ship_management': [('Operations Cockpit', 'cockpit'), ('Projects', 'projects'), ('Corrective / Survey', 'operations'), ('Survey Lifecycle', 'survey')],
    'owner': [('Fleet Cockpit', 'cockpit'), ('Projects', 'projects'), ('In-Service', 'operations'), ('Survey Lifecycle', 'survey')],
    'shipyard': [('NSC Cockpit', 'cockpit'), ('Projects', 'projects'), ('NSC Operations', 'operations'), ('Survey Lifecycle', 'survey')],
}

if role not in NAV:
    st.error("Your account has no valid EPAS workflow role. Contact the system administrator.")
    st.stop()

options = NAV[role]
state_key = f"epas_view_{role}_v414"
labels = [x[0] for x in options]
view_titles = {label: key for label, key in options}

project_id = st.session_state.get("selected_project_id")
if not project_id:
    with st.sidebar:
        st.markdown('<div class="psb-global-nav-label">GLOBAL NAVIGATION</div>', unsafe_allow_html=True)
        selected_label = st.radio("WORKSPACE", labels, index=0, key=state_key, label_visibility="collapsed")
        view = view_titles[selected_label]
        st.markdown('<div class="psb-sidebar-divider"></div>', unsafe_allow_html=True)
        if st.button("Sign out", key="global_signout_v413", use_container_width=True):
            from config.production_auth import sign_out
            sign_out()
            st.rerun()
else:
    view = "project_context"

render_topbar(user, "Project Workspace" if project_id else selected_label)

if project_id:
    render_project_workspace(role, project_id)
    st.stop()

if view == 'cockpit':
    render_role_cockpit(role)
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
