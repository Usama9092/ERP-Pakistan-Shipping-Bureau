"""PSB EPAS v4.1.3 — Project-specific role workspace.

A project click opens a dedicated project context. The project identity,
health, workflow state and role-specific actions remain visible while the
left project navigation changes by authenticated role.
"""
from __future__ import annotations

from datetime import date

import streamlit as st

from config import settings as cfg
from database import production_queries as pq
from utils import helpers as h

from components import certificates, reports, rfi_queue
from components import plan_appraisal_v414 as plan_appraisal

# Project navigation is intentionally project-specific and phase-aware.
# Once a project is opened, the left sidebar becomes the primary navigation for
# that project. The backend still enforces every role/phase permission.
PROJECT_NAV = [
    ("Project Overview", "overview", "Project health, phase status and next actions"),
    ("Plan Appraisal", "plan_appraisal", "Drawing appraisal, revision and approval"),
    ("NSC Survey", "nsc_survey", "New Construction Survey workflow"),
    ("In-Service Survey", "in_service", "Recurring In-Service survey cycles"),
    ("Survey Status", "survey_status", "Review-only live survey status for this project"),
    ("Risk Register", "risk_register", "Project risks and management decisions"),
    ("Governance & Acceptance", "governance", "Project governance, controlled releases, acceptance and closure"),
    ("Ship Register", "ship_register", "Review-only vessel/class/survey status for this project"),
    ("Certification", "certification", "Certificate lifecycle and issued certificates"),
    ("Documents", "documents", "Controlled project documents and releases"),
    ("Notifications", "notifications", "Project-specific notifications"),
    ("Audit Trail", "audit", "Project history and traceable activity"),
]

# Role labels remain visible in the project context header.
ROLE_LABELS = {
    "gm": "GM Classification",
    "dm": "Department Manager",
    "engineer": "Authorized Engineer",
    "surveyor": "Authorized Surveyor",
    "designer": "Designer · Stakeholder",
    "ship_management": "Ship Management · Stakeholder",
    "owner": "Owner · Stakeholder",
    "shipyard": "Shipyard · Stakeholder",
}

def _safe(fn, label="Project operation"):
    try:
        return fn()
    except Exception as exc:
        ref = abs(hash(f"{label}:{type(exc).__name__}")) % 100000
        st.error(f"{label} could not be loaded. Reference PSB-{ref:05d}.")
        return None

def open_project(project_id: str):
    st.session_state["selected_project_id"] = project_id
    st.session_state["project_nav_key"] = "overview"

def clear_project():
    st.session_state.pop("selected_project_id", None)
    st.session_state.pop("project_nav_key", None)

def render_project_launcher(role: str):
    """Role-safe project register. Only GM can create a project; all other roles may only open projects."""
    st.markdown('<div class="psb-section-eyebrow">PROJECT REGISTER</div>', unsafe_allow_html=True)
    head_left, head_actions = st.columns([4.3, 2.2])
    with head_left:
        st.markdown("<div class='page-title'>Projects</div>", unsafe_allow_html=True)
    with head_actions:
        if role == "gm":
            a1, a2 = st.columns(2)
            with a1:
                if st.button("+ Create Project", key="gm_create_project_from_projects", type="primary", use_container_width=True):
                    st.session_state["gm_create_project_open"] = True
                    st.session_state["gm_create_stakeholder_open"] = False
                    st.rerun()
            with a2:
                if st.button("+ Create New Stakeholder", key="gm_create_stakeholder_from_projects", type="secondary", use_container_width=True):
                    st.session_state["gm_create_stakeholder_open"] = True
                    st.session_state["gm_create_project_open"] = False
                    st.rerun()

    if role == "gm" and st.session_state.get("gm_create_stakeholder_open"):
        from components.stakeholder_registry import render as render_stakeholder_registry
        render_stakeholder_registry(role)
        st.stop()

    if role == "gm" and st.session_state.get("gm_create_project_open"):
        from components.gm_production import render_create_project
        with st.container(border=True):
            st.markdown("### Create Project")
            st.caption("GM-only action. Select registered Owner, Designer, Ship Management and Shipyard records for this project.")
            if st.button("Close", key="close_gm_create_project"):
                st.session_state["gm_create_project_open"] = False
                st.rerun()
            render_create_project()
        st.markdown("---")

    with st.expander("Authorized global search", expanded=False):
        search = st.text_input(
            "Search project, vessel, RFI or certificate",
            placeholder="Enter at least 2 characters",
            key=f"project_global_search_{role}",
        )
        if len(search.strip()) >= 2:
            results = _safe(lambda: pq.global_search_v36(search, 25), "Search") or []
            if not results:
                st.info("No authorized matches found.")
            for row in results:
                st.markdown(
                    f"**{str(row.get('result_type', '')).title()}** · {row.get('title', '—')}"
                )

    projects = _safe(lambda: pq.projects("active"), "Project register") or []

    if not projects:
        st.info("No projects are available to this account.")
        return

    for p in projects:
        health = _safe(
            lambda pid=p["id"]: pq.dashboard_project_health_bundle([pid]).get(pid),
            "Project health",
        ) or {}
        with st.container(border=True):
            left, mid, right = st.columns([4.2, 1.8, 1])
            with left:
                status = str(p.get("status","active")).replace("_"," ").title()
                phases = ", ".join(str(x).replace("_"," ").title() for x in (p.get("phases") or [])) or "Configured workflow"
                st.markdown(
                    f"<div class='psb-project-row-title'><span class='psb-project-code'>{p.get('project_code','—')}</span>"
                    f"<span class='psb-project-name'>{p.get('name','—')}</span>"
                    f"<span class='psb-project-status'>{status}</span></div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"{p.get('vessel_type','—')} · {p.get('flag_state','—')} · {phases}")
            with mid:
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Complete", f"{health.get('completion_pct',0)}%")
                mc2.metric("Overdue", health.get('overdue_tasks',0))
                mc3.metric("Open Obs.", health.get('open_observations',0))
            with right:
                if st.button("Open Project →", key=f"psb_open_project_{role}_{p['id']}", use_container_width=True, type="primary"):
                    open_project(p["id"])
                    st.rerun()

def render(role: str, project_id: str | None, nav_host=None):
    if not project_id:
        render_project_launcher(role)
        return

    project = _safe(lambda: pq.project(project_id), "Project") or None
    if not project:
        st.error("The selected project is unavailable or you are not authorized to view it.")
        if st.button("← Back to Projects"):
            clear_project()
            st.rerun()
        return

    vessel = _safe(lambda: pq.get_vessel_for_project(project_id), "Vessel particulars")
    health = _safe(lambda: pq.dashboard_project_health_bundle([project_id]).get(project_id), "Project health") or {}
    role_name = ROLE_LABELS.get(role, "Authenticated User")

    # Project identity bar
    st.markdown(
        f"""
        <div class="psb-project-header">
          <div class="psb-project-header__identity">
            <div class="psb-project-header__code">{project.get('project_code','—')}</div>
            <div class="psb-project-header__name">{project.get('name','—')}</div>
            <div class="psb-project-header__meta">
              {project.get('vessel_type','—')} · {project.get('flag_state','—')} · {role_name}
            </div>
          </div>
          <div class="psb-project-header__metrics">
            <span><b>{health.get('completion_pct',0)}%</b><small>completion</small></span>
            <span><b>{health.get('overdue_tasks',0)}</b><small>overdue</small></span>
            <span><b>{health.get('open_escalations',0)}</b><small>escalations</small></span>
            <span class="psb-project-health psb-project-health--{str(health.get('health_status','watch')).lower()}">
              {str(health.get('health_status','Watch')).title()}
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to Projects", key=f"back_projects_{role}", type="secondary"):
        clear_project()
        st.rerun()

    phases = {str(x).lower() for x in (project.get("phases") or [])}
    phase_rows = _safe(lambda: pq.project_phase_status(project_id), "Project phase status") or []
    phase_states = {
        str(row.get("phase") or "").lower(): str(row.get("status") or "").lower()
        for row in phase_rows
    }
    nsc_state = phase_states.get("nsc_survey", "")
    in_service_state = phase_states.get("in_service", "")
    in_service_unlocked = (
        "nsc_survey" not in phases
        or nsc_state in {"completed", "accepted", "closed"}
        or in_service_state in {"ready", "active", "in_progress", "completed"}
    )
    # Only phases actually included in the selected project are shown. This keeps
    # the project navigation honest: Plan/NSC/In-Service appear only when they
    # are part of that project's scope. Certification, Documents, Notifications
    # and Audit are always available within the project context.
    nav = []
    for label, value, desc in PROJECT_NAV:
        if value == "governance" and role not in {"gm", "dm"}:
            continue
        if role in {"designer", "engineer"} and value in {"nsc_survey", "survey_status"}:
            continue
        direct_in_service_plan = (
            "in_service" in phases
            and in_service_unlocked
            and role in {"gm", "owner", "ship_management"}
        )
        if value == "plan_appraisal" and "plan_appraisal" not in phases and not direct_in_service_plan:
            continue
        if value == "nsc_survey" and "nsc_survey" not in phases:
            continue
        if value == "in_service" and ("in_service" not in phases or not in_service_unlocked):
            continue
        nav.append((label, value, desc))

    labels = [x[0] for x in nav]
    values = {x[0]: x[1] for x in nav}
    descriptions = {x[0]: x[2] for x in nav}
    current = st.session_state.get("project_nav_key", "overview")
    if current not in values.values():
        current = "overview"
        st.session_state["project_nav_key"] = "overview"
    default_label = next((x[0] for x in nav if x[1] == current), labels[0])

    # Project-specific navigation uses the application's custom fixed rail.
    # Falling back to st.sidebar keeps the component reusable outside app.py.
    navigation_surface = nav_host if nav_host is not None else st.sidebar
    with navigation_surface:
        st.markdown('<div class="psb-project-nav-label">PROJECT NAVIGATION</div>', unsafe_allow_html=True)
        selected = st.radio(
            "PROJECT NAVIGATION",
            labels,
            index=labels.index(default_label) if default_label in labels else 0,
            key=f"project_sidebar_v413_{role}_{project_id}",
            label_visibility="collapsed",
        )
        st.session_state["project_nav_key"] = values[selected]
        st.markdown('<div class="psb-sidebar-divider"></div>', unsafe_allow_html=True)
        if st.button("Change Project", key=f"change_project_v413_{project_id}", use_container_width=True):
            clear_project()
            st.rerun()
        with st.container(key="psb_nav_signout"):
            if st.button("Sign out", key=f"project_signout_v413_{project_id}", use_container_width=True):
                from config.production_auth import sign_out
                sign_out()
                clear_project()
                st.rerun()


    st.markdown(
        f"<div class='psb-project-breadcrumb'>Projects <span>›</span> {project.get('project_code','—')} <span>›</span> {selected}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='psb-workspace-section-kicker'>{selected.upper()}</div>", unsafe_allow_html=True)
    _render_section(role, values[selected], project, vessel, health)

def _render_section(role, section, project, vessel, health):
    pid = project["id"]

    if section == "overview":
        _overview(role, project, vessel, health)
    elif section == "info":
        _info(project, vessel)
    elif section == "plan_appraisal":
        # One project record is shared by every authorised role.  The component
        # applies role-specific controls while keeping drawings, revisions,
        # observations, PDFs and correspondence in the selected project.
        plan_appraisal.render(project, role)
    elif section == "nsc_survey":
        workflow_tab, control_tab = st.tabs(["RFI Workflow", "Schedule & Control"])
        with workflow_tab:
            _survey(role, pid, phase_filter="nsc_survey")
        with control_tab:
            from components.professional_center_v36 import render_survey_control
            render_survey_control(pid)
    elif section == "in_service":
        workflow_tab, lifecycle_tab, control_tab = st.tabs([
            "RFI Workflow", "Recurring Lifecycle", "Schedule & Control"
        ])
        with workflow_tab:
            _survey(role, pid, phase_filter="in_service")
        with lifecycle_tab:
            from components.survey_lifecycle_v36 import render as render_survey_lifecycle
            render_survey_lifecycle(pid)
        with control_tab:
            from components.professional_center_v36 import render_survey_control
            render_survey_control(pid)
    elif section == "survey_status":
        _survey_status(role, pid, project, vessel, health)
    elif section == "risk_register":
        _risk_register(pid, role)
    elif section == "ship_register":
        _ship_register(pid, vessel)
    elif section == "certification":
        # Owners may review and download issued certificates, but certificate
        # generation is an internal classification-authority action.
        certificates.render_for_project(pid, allow_generate=role != "owner")
    elif section == "milestones":
        _milestones(pid)
    elif section == "observations":
        _observations(pid)
    elif section == "documents" or section == "approved":
        _documents(role, pid, approved_only=(section == "approved"))
    elif section == "governance":
        if role == "gm":
            from components.governance_v15 import render_gm
            render_gm(pid)
        else:
            from components.professional_center_v36 import render_governance
            from components.survey_lifecycle_v36 import render_role_acceptance
            render_governance(pid)
            render_role_acceptance()
    elif section == "audit":
        _audit(pid)
    elif section == "work":
        _work(role, pid)
    elif section == "resources":
        _resources(pid)
    elif section == "corrective":
        _corrective(pid)
    elif section == "coordination":
        from components.professional_center_v36 import render_phase_and_coordination
        render_phase_and_coordination(pid)
    elif section == "revisions":
        _project_task_snapshot(pid, "Revision Requests")
    elif section == "notifications":
        _notifications(pid)
    elif section == "evidence":
        _corrective(pid, evidence_mode=True)
    elif section == "followup":
        _survey(role, pid, followup_only=True)
    elif section == "approved":
        _documents(role, pid, approved_only=True)


def _in_service_plan_submission(role: str, project: dict) -> None:
    """Project-scoped alteration/repair plan intake for authorized stakeholders."""
    pid = project["id"]
    st.markdown("### In-Service Plan Appraisal")
    st.caption(
        "Submit alteration, repair or modification drawings for this vessel. "
        "The plan is routed to GM intake and remains linked to this project through every revision."
    )

    with st.expander("Submit a plan to GM Intake", expanded=True):
        c1, c2 = st.columns(2)
        drawing_no = c1.text_input("Drawing number", key=f"is_plan_no_{role}_{pid}")
        title = c2.text_input("Drawing title", key=f"is_plan_title_{role}_{pid}")
        discipline = st.selectbox(
            "Discipline",
            ["Hull & Structure", "Machinery", "Electrical", "Stability", "Safety Equipment", "Fire & LSA"],
            key=f"is_plan_discipline_{role}_{pid}",
        )
        drawing_file = st.file_uploader(
            "Controlled drawing PDF",
            type=["pdf"],
            key=f"is_plan_file_{role}_{pid}",
        )
        note = st.text_area(
            "Submission purpose / modification scope",
            key=f"is_plan_note_{role}_{pid}",
        )
        if st.button(
            "Submit plan to GM →",
            type="primary",
            key=f"is_plan_submit_{role}_{pid}",
        ):
            if not drawing_no.strip() or not title.strip() or not drawing_file or not note.strip():
                st.error("Drawing number, title, PDF and modification scope are required.")
            elif _safe(
                lambda: pq.designer_submit_initial_drawing(
                    pid, drawing_no, title, discipline, drawing_file, note
                ),
                "Plan submission",
            ):
                st.success("Plan submitted and received in this project's GM Plan Appraisal intake.")
                st.rerun()

    drawings = _safe(lambda: pq.plan_drawings(pid), "Submitted plans") or []
    st.markdown("#### Plans submitted for this project")
    if not drawings:
        st.info("No in-service plans have been submitted yet.")
    for drawing in drawings:
        with st.container(border=True):
            revision = drawing.get("current_revision", drawing.get("revision", 1))
            st.markdown(
                f"**{drawing.get('drawing_no', 'Plan')} — {drawing.get('title', 'Untitled')}** · Rev {revision}"
            )
            st.caption(
                f"{str(drawing.get('discipline') or '—')} · "
                f"{str(drawing.get('status') or 'submitted').replace('_', ' ').title()}"
            )

def _overview(role, project, vessel, health):
    """Project landing page matching the PSB reference: no workflow snapshot and no recent activity."""
    pid = project["id"]
    st.markdown("### Project Overview")
    st.caption(f"Projects  ›  {project.get('project_code','—')}  ›  Overview")
    phase_rows = _safe(lambda: pq.project_phase_status(pid), "Phase status") or []
    tasks = _safe(lambda: pq.tasks(statuses=["pending","accepted","in_progress"], project_id=pid), "Project tasks") or []
    ship_rows = _safe(lambda: pq.ship_register_project(pid), "Survey status") or []
    ship = ship_rows[0] if ship_rows else (vessel or {})
    certs = _safe(lambda: pq.certificates(pid), "Project certificates") or []
    milestones = _safe(lambda: pq.project_milestones(pid), "Project milestones") or []
    priority = _safe(lambda: [r for r in (pq.my_work_queue() or []) if str(r.get("project_id")) == str(pid)], "Priority actions") or []

    next_due = health.get("next_survey_due") or ship.get("next_survey_due") or "—"
    survey_status = ship.get("survey_status") or health.get("survey_status") or "—"
    cert_expiring = len([c for c in certs if str(c.get("status","")).lower() in ("expiring","expiring_soon")])

    cards = [
        ("Project Health", f"{health.get('completion_pct',0)}%", str(health.get('health_status','—')).title(), "green"),
        ("Survey Due", str(next_due), str(survey_status).replace("_"," ").title(), "blue"),
        ("Open Observations", str(health.get('open_observations',0)), "Requires attention" if health.get('open_observations',0) else "None open", "amber"),
        ("Certificates", str(len(certs)), f"{cert_expiring} expiring soon" if cert_expiring else "Current", "teal"),
        ("Overdue Tasks", str(health.get('overdue_tasks',0)), "Requires attention" if health.get('overdue_tasks',0) else "On track", "red"),
    ]
    cols=st.columns(5)
    for col,(label,value,foot,tone) in zip(cols,cards):
        with col:
            st.markdown(
                f"<div class='ref-kpi ref-kpi--{tone}'><div class='ref-kpi__label'>{label}</div>"
                f"<div class='ref-kpi__value'>{value}</div><div class='ref-kpi__foot'>{foot}</div></div>",
                unsafe_allow_html=True,
            )

    left, mid, right = st.columns([1.2,1.15,1.0])
    with left:
        _project_panel_open("PROJECT LIFECYCLE & PHASE", "Scope-aware project progress")
        for p in phase_rows:
            status=str(p.get("status","")).upper()
            icon={"COMPLETED":"✓","IN_PROGRESS":"→","READY":"●","LOCKED":"○","BLOCKED":"!"}.get(status,"•")
            st.markdown(f"**{icon} {str(p.get('phase','')).replace('_',' ').title()}**")
            st.caption(p.get("gate_note") or status.replace("_"," ").title())
        if not phase_rows:
            st.info("No phase records are available.")
        _project_panel_close()
    with mid:
        _project_panel_open("SURVEY STATUS", "Review-only live status for this project")
        rows = ship_rows or ([ship] if ship else [])
        if rows:
            for r in rows[:4]:
                st.markdown(f"**{r.get('name') or project.get('name') or 'Vessel'}**")
                st.caption(f"Class: {r.get('class_status') or '—'} · Survey: {str(r.get('survey_status') or '—').replace('_',' ').title()}")
                st.caption(f"Next survey: {r.get('next_survey_due') or next_due}")
        else:
            st.info("Survey status is not yet available.")
        if st.button("View Survey Status →", key=f"overview_survey_status_{pid}"):
            st.session_state["project_nav_key"]="survey_status"; st.rerun()
        _project_panel_close()
    with right:
        _project_panel_open("MY PRIORITY ACTIONS", "Current work inside this project")
        if not priority:
            st.success("No immediate assigned actions.")
        else:
            for r in priority[:6]:
                st.markdown(f"**{str(r.get('task_type','Task')).replace('_',' ').title()}**")
                st.caption(f"{r.get('sla_state') or 'ON_TRACK'} · due {r.get('sla_due_at') or r.get('due_at') or '—'}")
        if priority and st.button("Open My Project Work →", key=f"overview_work_{pid}"):
            st.session_state["project_nav_key"]="work"; st.rerun()
        _project_panel_close()

    bottom_left, bottom_mid = st.columns([1.2,1.0])
    with bottom_left:
        _project_panel_open("MILESTONE STATUS", "Plan, NSC and In-Service milestones")
        if not milestones:
            st.info("No project milestones are available.")
        else:
            for m in milestones[:10]:
                status=str(m.get("status","pending")).replace("_"," ").title()
                st.markdown(f"**{m.get('name') or m.get('milestone_code') or 'Milestone'}** · {status}")
                st.caption(f"Due {m.get('due_date') or '—'}")
        _project_panel_close()
    with bottom_mid:
        _project_panel_open("CERTIFICATES OVERVIEW", "Current controlled project certificates")
        if not certs:
            st.info("No certificates issued.")
        else:
            for cert in certs[:5]:
                st.markdown(f"**{cert.get('cert_number','—')}** · {str(cert.get('cert_type','—')).replace('_',' ').title()}")
                st.caption(f"Status {str(cert.get('status','—')).title()} · Expiry {cert.get('expiry_date') or '—'}")
        if certs and st.button("View all Certificates →", key=f"overview_certificates_{pid}"):
            st.session_state["project_nav_key"]="certification"; st.rerun()
        _project_panel_close()
    with st.container(border=True):
        st.markdown("#### PROJECT SUMMARY")
        summary = [
            ("Project ID", project.get("project_code")),
            ("Vessel", project.get("name")),
            ("Classification No.", project.get("classification_number")),
            ("Current Phase", health.get("current_phase") or ("In-Service Active" if "in_service" in {str(x).lower() for x in project.get("phases",[]) } else "—")),
            ("Current Cycle", health.get("current_cycle") or "—"),
            ("Next Survey", next_due),
        ]
        sc=st.columns(3)
        for i,(k,v) in enumerate(summary):
            sc[i%3].markdown(f"**{k}**")
            sc[i%3].caption(v or "—")

def _project_panel_open(title, subtitle=''):
    st.markdown(
        f"<div class='psb-project-panel'><div class='psb-project-panel__title'>{title}</div><div class='psb-project-panel__subtitle'>{subtitle}</div>",
        unsafe_allow_html=True,
    )

def _project_panel_close():
    st.markdown("</div>", unsafe_allow_html=True)

def _survey_status(role, pid, project, vessel, health):
    st.markdown("### Survey Status")
    st.caption("Review-only project survey status. Values are refreshed from the controlled project and vessel records.")
    phase_rows = _safe(lambda: pq.project_phase_status(pid), "Survey phase status") or []
    current_cycle = health.get("current_cycle") or "—"
    next_due = health.get("next_survey_due") or (vessel.get("next_survey_due") if vessel else None) or "—"
    c = st.columns(6)
    c[0].metric("Current Phase", str(health.get("current_phase") or "—").replace("_"," " ).title())
    c[1].metric("Current Cycle", current_cycle)
    c[2].metric("Last Survey", (vessel or {}).get("last_survey_date") or "—")
    c[3].metric("Next Survey Due", next_due)
    c[4].metric("Open Observations", health.get("open_observations", 0))
    c[5].metric("Overdue Tasks", health.get("overdue_tasks", 0))

    st.markdown("#### Due Certificates")
    certs = _safe(lambda: pq.certificates(pid), "Due certificates") or []
    certs = sorted(certs, key=lambda row: str(row.get("expiry_date") or "9999-12-31"))
    if not certs:
        st.info("No certificates have been issued for this project.")
    for cert in certs:
        expiry = cert.get("expiry_date")
        status = str(cert.get("status") or "active").replace("_", " ").title()
        cols = st.columns([1.7, 1.5, 1.25, 1.2])
        cols[0].markdown(f"**{cert.get('cert_number') or 'Certificate'}**")
        cols[1].write(str(cert.get("cert_type") or "—").replace("_", " ").title())
        cols[2].write(f"Due: {expiry or '—'}")
        cols[3].write(status)

    stakeholder_phases = {
        "owner": ("in_service", "In-Service Survey"),
        "ship_management": ("in_service", "In-Service Survey"),
        "shipyard": ("nsc_survey", "NSC Survey"),
    }
    if role in stakeholder_phases and vessel:
        phase, default_type = stakeholder_phases[role]
        with st.expander("Request an RFI", expanded=False):
            st.caption("Authorized requests are submitted to GM Intake for review and allocation.")
            survey_type = st.text_input(
                "Survey type",
                value=default_type,
                key=f"project_status_rfi_type_{role}_{pid}",
            )
            due_value = next_due if next_due != "—" else date.today()
            try:
                due_value = due_value if isinstance(due_value, date) else date.fromisoformat(str(due_value)[:10])
            except (TypeError, ValueError):
                due_value = date.today()
            requested_date = st.date_input(
                "Requested survey date",
                value=due_value,
                key=f"project_status_rfi_date_{role}_{pid}",
            )
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                index=1,
                key=f"project_status_rfi_priority_{role}_{pid}",
            )
            scope = st.text_area(
                "Survey scope / request details",
                key=f"project_status_rfi_scope_{role}_{pid}",
            )
            if st.button(
                "Submit RFI to GM Intake →",
                type="primary",
                key=f"project_status_rfi_submit_{role}_{pid}",
            ):
                if not survey_type.strip() or not scope.strip():
                    st.error("Survey type and request details are required.")
                elif _safe(
                    lambda: pq.stakeholder_create_rfi(
                        pid, vessel["id"], phase, survey_type, requested_date, priority, scope
                    ),
                    "RFI request",
                ):
                    st.success("RFI submitted successfully and received by GM Intake.")
                    st.rerun()

    st.markdown("#### Project Phase Status")
    for row in phase_rows:
        status = str(row.get("status","—")).replace("_"," " ).title()
        st.markdown(f"**{str(row.get('phase','—')).replace('_',' ').title()}** · {status}")
        st.progress(1.0 if status == "Completed" else 0.6 if status in ("In Progress","Ready") else 0.0)

    rfi_rows = _safe(lambda: pq.list_rfis(project_id=pid), "Project survey status") or []
    if rfi_rows:
        st.markdown("#### Survey / RFI Register")
        for r in rfi_rows[:30]:
            phase = str(r.get("phase","")).replace("_"," " ).title()
            status = str(r.get("status","")).replace("_"," " ).title()
            st.markdown(f"**{r.get('rfi_code','RFI')}** · {phase} · {status}")
            st.caption(f"Requested {r.get('requested_date') or '—'} · Priority {str(r.get('priority','—')).title()}")
    else:
        st.info("No survey RFI records are currently available.")

def _risk_register(pid, role):
    st.markdown("### Risk Register")
    rows = _safe(lambda: pq.risks(pid, open_only=False), "Project risk register") or []
    if not rows:
        st.success("No project risks are currently registered.")
    for r in rows:
        st.markdown(f"**{r.get('risk_code','RISK')} · {r.get('title','Untitled')}** · {str(r.get('severity','')).upper()} · {str(r.get('status','')).replace('_',' ').title()}")
        st.caption(f"{r.get('mitigation') or 'No mitigation recorded.'}")
    if role in ("gm", "dm"):
        st.caption("GM/DM may add or update risks through the controlled governance controls.")

def _ship_register(pid, vessel):
    st.markdown("### Ship Register")
    st.caption("Review-only vessel/class/survey status for this selected project. The register is updated from controlled survey and certificate activity.")
    rows = _safe(lambda: pq.ship_register_project(pid), "Ship Register") or []
    if not rows and vessel:
        rows = [{
            "project_id": pid, "vessel_id": vessel.get("id"), "name": vessel.get("name"),
            "class_status": vessel.get("class_status") or vessel.get("current_class"),
            "survey_status": vessel.get("survey_status"), "next_survey_due": vessel.get("next_survey_due")
        }]
    if not rows:
        st.info("No vessel record is available for this project.")
        return
    for r in rows:
        c = st.columns([2.0,1.25,1.25,1.45,1.45])
        c[0].markdown(f"**{r.get('name') or 'Vessel'}**")
        c[0].caption(f"Vessel ID {r.get('vessel_id') or '—'}")
        c[1].write(f"Class: {r.get('class_status') or '—'}")
        c[2].write(f"Survey: {str(r.get('survey_status') or '—').replace('_',' ').title()}")
        c[3].write(f"Next Due: {r.get('next_survey_due') or '—'}")
        certs = _safe(lambda vid=r.get('vessel_id'): pq.list_certificates(vessel_id=vid), "Ship Register certificates") or []
        c[4].write(f"Certificates: {len(certs)}")
        st.markdown("<hr class='divider-hr' style='margin:6px 0;'>", unsafe_allow_html=True)


def _info(project, vessel):
    st.markdown("### Project Information")
    c1, c2 = st.columns([1.25, 1])
    with c1:
        with st.container(border=True):
            st.markdown("#### Vessel particulars")
            rows = [
                ("Project code", project.get("project_code")),
                ("Vessel", project.get("name")),
                ("Vessel type", project.get("vessel_type")),
                ("Flag", project.get("flag_state")),
                ("Classification No.", project.get("classification_number")),
                ("Register No.", project.get("register_number")),
                ("Contract No.", project.get("contract_number")),
                ("Classification scope", project.get("classification_scope")),
                ("Classification request", project.get("classification_request")),
            ]
            for k,v in rows:
                a,b = st.columns([1,1.5])
                a.caption(k); b.write(v or "—")
        if vessel:
            with st.container(border=True):
                st.markdown("#### Principal particulars")
                for k,v in [
                    ("IMO / Reg.", vessel.get("imo_number")),
                    ("LOA", f"{vessel.get('loa_m')} m" if vessel.get('loa_m') else "—"),
                    ("Beam", f"{vessel.get('beam_m')} m" if vessel.get('beam_m') else "—"),
                    ("Draft", f"{vessel.get('draft_m')} m" if vessel.get('draft_m') else "—"),
                    ("Power", f"{vessel.get('power_kw')} kW" if vessel.get('power_kw') else "—"),
                    ("Speed", f"{vessel.get('speed_knots')} kn" if vessel.get('speed_knots') else "—"),
                ]:
                    a,b = st.columns([1,1.5]); a.caption(k); b.write(v or "—")
    with c2:
        with st.container(border=True):
            st.markdown("#### Role within this project")
            st.success(ROLE_LABELS.get(pq.profile().get("role"), "Authenticated role"))
            st.caption("Permissions and available actions are enforced by the authenticated role and project membership.")
        with st.container(border=True):
            st.markdown("#### Project phases")
            for ph in project.get("phases",[]):
                st.write("•", str(ph).replace("_"," ").title())

def _survey(role, pid, followup_only=False, phase_filter: str | None = None):
    try:
        phase_label = {"nsc_survey": "NSC Survey", "in_service": "In-Service Survey"}.get(phase_filter, "Survey / RFI")
        st.caption(f"{phase_label} follows the controlled GM → DM → Surveyor → DM → GM workflow.")
        if followup_only:
            st.info("Follow-up RFI view — controlled corrective-action loop.")
        if phase_filter:
            st.markdown(f"**Current survey phase:** {phase_label}")
        # The queue contract requires an explicit lifecycle phase.  Passing the
        # selected project tab's phase prevents the deployed NSC/In-Service
        # workspace from failing with a missing ``phase`` argument.
        rfi_queue.render(phase=phase_filter or cfg.PHASE_NSC_SURVEY, project_id=pid)
    except Exception as exc:
        st.error(f"Survey workspace unavailable: {exc}")

def _work(role, pid):
    rows = _safe(lambda: pq.tasks(statuses=["pending","accepted","in_progress"], project_id=pid), "My project work") or []
    user = pq.profile()
    rows = [r for r in rows if str(r.get("to_user_id")) == str(user.get("id"))]
    if not rows:
        st.success("No assigned project tasks.")
        return
    for r in rows[:100]:
        state = r.get("sla_state") or "ON_TRACK"
        st.markdown(
            f"<div class='psb-task-row'><b>{str(r.get('task_type','Task')).replace('_',' ').title()}</b>"
            f"<span class='psb-task-state psb-task-state--{str(state).lower()}'>{state}</span></div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Due {r.get('sla_due_at') or r.get('due_at') or '—'} · {r.get('note') or ''}")

def _milestones(pid):
    rows = _safe(lambda: pq.project_milestones(pid), "Project milestones") or []
    if not rows:
        st.info("No project milestones are available.")
        return
    for r in rows:
        state = str(r.get("status","")).replace("_"," ").title()
        st.markdown(f"**{r.get('name') or r.get('milestone_code') or 'Milestone'}** · {state}")
        st.caption(f"Due {r.get('due_date') or '—'} · {r.get('gate_note') or ''}")

def _observations(pid):
    rows = _safe(lambda: pq.observations_for_project(pid), "Project observations") or []
    if not rows:
        st.success("No project observations are currently visible.")
        return
    for r in rows[:150]:
        state = str(r.get("status","open")).upper()
        st.markdown(
            f"**{r.get('obs_code','Observation')}** · {r.get('severity','—')} · {state}"
        )
        st.caption(
            f"{r.get('description','—')} · Rule {r.get('rule_reference') or '—'} · "
            f"Location {r.get('location') or '—'}"
        )

def _documents(role, pid, approved_only=False):
    rows = _safe(lambda: pq.list_documents(pid), "Project documents") or []
    if approved_only:
        rows = [r for r in rows if str(r.get("release_status","")).lower() in ("released","approved") or r.get("status") in ("approved","released")]
    if not rows:
        st.info("No documents are currently visible in this project workspace.")
        return
    for r in rows[:150]:
        st.markdown(f"**{r.get('file_name','Document')}** · {r.get('version','—')} · {r.get('release_status') or r.get('status') or '—'}")
        st.caption(f"{r.get('category','—')} · {r.get('uploaded_at','—')}")

def _audit(pid):
    rows = _safe(lambda: pq.project_timeline_v35(pid,100), "Project audit") or []
    if not rows:
        st.info("No project history is available.")
        return
    for r in rows:
        st.caption(f"{r.get('occurred_at') or r.get('created_at') or '—'} · {r.get('actor_role','system')} · {r.get('event_type','')} · {r.get('summary') or r.get('note') or '—'}")

def _resources(pid):
    try:
        from components.professional_center_v36 import render_sla
        render_sla(pid)
    except Exception as exc:
        st.error(str(exc))

def _corrective(pid, evidence_mode=False):
    rows = _safe(lambda: pq.corrective_actions(project_id=pid), "Corrective actions") or []
    if not rows:
        st.success("No corrective actions are currently visible.")
        return
    for r in rows[:100]:
        st.markdown(f"**{r.get('action_code') or r.get('id','Corrective Action')}** · {str(r.get('status','')).replace('_',' ').title()}")
        st.caption(r.get("instruction") or "No instruction recorded.")

def _notifications(pid):
    rows = _safe(pq.notifications, "Notifications") or []
    rows = [r for r in rows if not pid or str(r.get("project_id")) == str(pid)]
    if not rows:
        st.success("No project notifications.")
        return
    for r in rows[:100]:
        st.markdown(f"**{r.get('title','Notification')}**")
        st.caption(r.get('body') or '')

def _project_task_snapshot(pid, title):
    rows = _safe(lambda: pq.tasks(statuses=["pending","accepted","in_progress"], project_id=pid), title) or []
    st.markdown(f"### {title}")
    if not rows:
        st.info(f"No {title.lower()} tasks are currently visible.")
        return
    for r in rows[:100]:
        st.write(f"**{str(r.get('task_type','Task')).replace('_',' ').title()}**")
        st.caption(r.get('note') or '—')

