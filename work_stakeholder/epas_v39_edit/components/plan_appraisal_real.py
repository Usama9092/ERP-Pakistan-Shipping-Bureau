"""PSB Plan Appraisal · production single-tab master/detail workspace.

This surface renders persisted Supabase records only. It never seeds sample plans,
creates fake PDFs, or substitutes demo data. Each drawing opens its own revision
package: Designer source PDF + PSB Engineer marked-up drawing + Design Appraisal
Report, remarks, assignments and immutable workflow history.
"""
from __future__ import annotations

import html
from collections import defaultdict

import streamlit as st

from config import settings as cfg
from config.supabase_client import is_demo_mode
from database import production_queries as pq
from database import real_plan_queries as rpq

STATUS_LABELS = {
    "submitted": "Submitted",
    "assigned_manager": "Manager Assigned",
    "assigned_engineer": "Engineer Assigned",
    "under_engineer_review": "Engineer Review",
    "observation_raised": "Remarks Issued",
    "designer_response": "Designer Response Required",
    "revision_pending_dm": "Revision Pending Manager",
    "review_resubmitted": "Re-appraisal",
    "manager_review": "Manager Review",
    "surveyor_verification_pending": "Surveyor Verification",
    "pending_gm_approval": "Pending GM Approval",
    "approved": "Approved",
    "rejected": "Returned / Rejected",
}

DISCIPLINES = ["Stability", "Hull & Structure", "Machinery", "Electrical", "Fire & LSA", "Fire Safety"]


def _label(status: str | None) -> str:
    return STATUS_LABELS.get(str(status or ""), str(status or "—").replace("_", " ").title())


def _safe(action, label: str):
    try:
        return action()
    except Exception as exc:
        st.error(f"{label} failed: {exc}")
        return None


def _open_file(path: str, label: str, key: str):
    try:
        url = rpq.signed_storage_url(path)
        st.link_button(label, url, key=key, use_container_width=True)
    except Exception as exc:
        st.warning(f"Controlled file is unavailable: {exc}")


def render(project: dict | None = None, role: str | None = None) -> None:
    if is_demo_mode():
        st.error("Real Plan Appraisal is disabled in demo mode. Configure production Supabase and sign in with a project account.")
        return

    if project is None:
        project_id = st.session_state.get("selected_project_id")
        project = pq.project(project_id) if project_id else None
    if not project:
        st.warning("Select a project first.")
        return

    actor = pq.profile()
    role = role or actor.get("role", "readonly")
    project_id = project["id"]
    drawings = _safe(lambda: rpq.register(project_id), "Plan register") or []

    st.markdown('<div class="section-title">Plan Appraisal</div>', unsafe_allow_html=True)
    st.caption(f"{project.get('project_code','—')} · Real controlled drawings, revisions, appraisal files and decisions from Supabase")

    _kpis(drawings)
    if role == cfg.ROLE_DESIGNER:
        _designer_new_plan(project)

    if not drawings:
        st.info("No plan has been submitted for this project. The register will populate when the Designer submits the first controlled PDF.")
        return

    left, right = st.columns([3.5, 6.5], gap="medium")
    with left:
        selected_id = _master_register(drawings, project_id)
    if not selected_id:
        return
    drawing = next((row for row in drawings if str(row["drawing_id"]) == str(selected_id)), None)
    if not drawing:
        return
    with right:
        _detail_workspace(drawing, role, actor, project)


def _kpis(drawings: list[dict]) -> None:
    total = len(drawings)
    approved = sum(1 for d in drawings if d.get("status") == "approved")
    open_remarks = sum(int(d.get("open_remarks") or 0) for d in drawings)
    pending_gm = sum(1 for d in drawings if d.get("status") == "pending_gm_approval")
    completion = round((approved / total) * 100) if total else 0
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Plans", total)
    c2.metric("Approved", approved)
    c3.metric("Completion", f"{completion}%")
    c4.metric("Open Remarks", open_remarks)
    c5.metric("Pending GM", pending_gm)


def _master_register(drawings: list[dict], project_id: str) -> str | None:
    st.markdown("### Plan Register")
    search = st.text_input("Search", placeholder="Drawing no., title, discipline…", key=f"real_pa_search_{project_id}").strip().lower()
    statuses = sorted({_label(d.get("status")) for d in drawings})
    status_filter = st.selectbox("Status", ["All", *statuses], key=f"real_pa_status_{project_id}")

    filtered = []
    for row in drawings:
        haystack = " ".join(str(row.get(k) or "") for k in ("drawing_no", "title", "discipline", "current_file_name")).lower()
        if search and search not in haystack:
            continue
        if status_filter != "All" and _label(row.get("status")) != status_filter:
            continue
        filtered.append(row)

    if not filtered:
        st.info("No plans match the current filter.")
        return None

    groups: dict[str, list[dict]] = defaultdict(list)
    for row in filtered:
        groups[str(row.get("discipline") or "Other")].append(row)

    ids = [str(row["drawing_id"]) for row in filtered]
    current = st.session_state.get(f"real_pa_selected_{project_id}")
    if current not in ids:
        current = ids[0]
        st.session_state[f"real_pa_selected_{project_id}"] = current

    for discipline in sorted(groups):
        with st.expander(f"{discipline} · {len(groups[discipline])}", expanded=True):
            for row in groups[discipline]:
                did = str(row["drawing_id"])
                prefix = "●" if did == current else "○"
                label = f"{prefix} {row.get('drawing_no','—')} · {row.get('title','Untitled')} · Rev {row.get('current_revision',1)} · {_label(row.get('status'))}"
                if st.button(label, key=f"real_pa_pick_{did}", use_container_width=True):
                    st.session_state[f"real_pa_selected_{project_id}"] = did
                    st.rerun()
    return st.session_state.get(f"real_pa_selected_{project_id}")


def _detail_workspace(d: dict, role: str, actor: dict, project: dict) -> None:
    st.markdown(f"### {html.escape(str(d.get('drawing_no','—')))} · {html.escape(str(d.get('title','Untitled')))}")
    st.caption(f"{d.get('discipline','—')} · Rev {d.get('current_revision',1)} · {_label(d.get('status'))}")

    m1, m2, m3 = st.columns(3)
    m1.markdown(f"**Designer**\n\n{d.get('designer_name') or 'Unassigned'}")
    m2.markdown(f"**Plan Appraisal Manager**\n\n{d.get('manager_name') or 'Unassigned'}")
    m3.markdown(f"**Plan Appraisal Engineer**\n\n{d.get('engineer_name') or 'Unassigned'}")

    package = _safe(lambda: rpq.revision_package(str(d["drawing_id"])), "Revision package") or []
    remarks = _safe(lambda: rpq.observations(str(d["drawing_id"])), "Remarks") or []
    events = _safe(lambda: rpq.events(str(d["drawing_id"])), "Workflow history") or []

    overview_tab, files_tab, remarks_tab, history_tab = st.tabs([
        "Overview & Action", "Designer / Appraisal Files", "Remarks & Responses", "Audit History"
    ])
    with overview_tab:
        _workflow_action(d, role, actor, project)
    with files_tab:
        _revision_files(d, package)
    with remarks_tab:
        _remarks(remarks)
    with history_tab:
        _history(events)


def _revision_files(d: dict, package: list[dict]) -> None:
    if not package:
        st.info("No persisted revision package is available for this drawing yet.")
        return
    by_rev: dict[int, list[dict]] = defaultdict(list)
    for row in package:
        by_rev[int(row.get("revision_no") or 0)].append(row)

    for revision_no in sorted(by_rev, reverse=True):
        rows = by_rev[revision_no]
        base = rows[0]
        current = " · CURRENT" if revision_no == int(d.get("current_revision") or 0) else ""
        with st.container(border=True):
            st.markdown(f"#### Revision {revision_no}{current}")
            st.caption(f"Submitted by {base.get('submitted_by_name') or 'Designer'} · {base.get('submitted_at') or '—'} · {str(base.get('revision_status') or 'submitted').replace('_',' ').title()}")
            if base.get("submission_note"):
                st.write(base["submission_note"])

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Designer Submission**")
                st.write(base.get("designer_file_name") or "No designer file registered")
                if base.get("designer_storage_path"):
                    _open_file(base["designer_storage_path"], "Open Designer PDF", f"designer_pdf_{base['revision_id']}")
                if base.get("designer_sha256"):
                    st.caption(f"SHA-256 · {base['designer_sha256'][:18]}…")
            with c2:
                st.markdown("**PSB Engineer Appraisal**")
                artifacts = [r for r in rows if r.get("artifact_id")]
                if not artifacts:
                    st.info("No Engineer appraisal file has been registered against this revision.")
                for artifact in artifacts:
                    kind = "Marked-up / Appraised Drawing" if artifact.get("artifact_type") == "MARKED_UP_DRAWING" else "Design Appraisal Report"
                    st.write(f"**{kind}** · {artifact.get('artifact_file_name','—')}")
                    st.caption(f"Uploaded by {artifact.get('artifact_uploaded_by_name') or 'Engineer'} · {artifact.get('artifact_uploaded_at') or '—'} · {artifact.get('artifact_status') or 'submitted'}")
                    if artifact.get("artifact_storage_path"):
                        _open_file(artifact["artifact_storage_path"], f"Open {kind}", f"artifact_{artifact['artifact_id']}")


def _remarks(rows: list[dict]) -> None:
    if not rows:
        st.success("No technical remarks are recorded against this drawing.")
        return
    for row in rows:
        with st.container(border=True):
            st.markdown(f"**{row.get('obs_code','Remark')}** · {row.get('severity','—')} · {str(row.get('status','open')).title()}")
            st.write(row.get("description") or "—")
            if row.get("clause_reference"):
                st.caption(f"Rule / clause: {row['clause_reference']}")
            if row.get("drawing_reference"):
                st.caption(f"Drawing reference: {row['drawing_reference']}")
            if row.get("response"):
                st.info(f"Designer response: {row['response']}")


def _history(rows: list[dict]) -> None:
    if not rows:
        st.info("No workflow event has been recorded yet.")
        return
    for row in rows:
        actor = _safe(lambda uid=row.get("actor_id"): rpq.profile_name(uid), "Actor lookup") or "System"
        st.markdown(f"**{str(row.get('event_type') or 'Event').replace('_',' ').title()}** · {actor}")
        st.caption(f"{row.get('created_at') or '—'} · {row.get('from_status') or '—'} → {row.get('to_status') or '—'}")
        if row.get("note"):
            st.write(row["note"])


def _designer_new_plan(project: dict) -> None:
    with st.expander("+ Submit New Plan", expanded=False):
        st.caption("The uploaded PDF becomes the real Revision 1 for this project. No placeholder file is generated.")
        c1, c2 = st.columns(2)
        drawing_no = c1.text_input("Drawing number", key=f"real_new_no_{project['id']}")
        title = c2.text_input("Drawing title", key=f"real_new_title_{project['id']}")
        discipline = st.selectbox("Discipline", DISCIPLINES, key=f"real_new_disc_{project['id']}")
        pdf = st.file_uploader("Designer drawing PDF · Revision 1", type=["pdf"], key=f"real_new_pdf_{project['id']}")
        note = st.text_area("Designer transmittal / submission note", key=f"real_new_note_{project['id']}")
        if st.button("Submit Revision 1", type="primary", key=f"real_new_submit_{project['id']}"):
            if not drawing_no.strip() or not title.strip() or not note.strip() or pdf is None:
                st.error("Drawing number, title, PDF and submission note are required.")
            elif _safe(lambda: rpq.submit_initial(project["id"], drawing_no.strip(), title.strip(), discipline, pdf, note.strip()), "Plan submission"):
                st.success("Revision 1 registered and routed into Plan Appraisal.")
                st.rerun()


def _workflow_action(d: dict, role: str, actor: dict, project: dict) -> None:
    status = str(d.get("status") or "")
    drawing_id = str(d["drawing_id"])
    st.markdown("#### Current workflow action")

    if role == cfg.ROLE_GM and status == "submitted":
        members = rpq.project_members(project["id"])
        managers = []
        for m in members:
            p = m.get("profiles") or m.get("profile") or {}
            if (m.get("role") == cfg.ROLE_DM or p.get("role") == cfg.ROLE_DM) and p.get("id"):
                managers.append(p)
        if not managers:
            st.warning("No Plan Appraisal Manager is assigned to this project.")
            return
        by_id = {str(x["id"]): x for x in managers}
        selected = st.selectbox("Plan Appraisal Manager", list(by_id), format_func=lambda x: by_id[x].get("full_name") or x, key=f"real_mgr_{drawing_id}")
        if st.button("Assign Manager", type="primary", key=f"real_assign_mgr_{drawing_id}"):
            if _safe(lambda: rpq.assign_manager(drawing_id, selected), "Manager assignment"):
                st.rerun()
        return

    if role == cfg.ROLE_DM and status in {"assigned_manager", "revision_pending_dm"}:
        engineers = _safe(lambda: rpq.eligible_engineers(project["id"], str(d.get("discipline") or "")), "Engineer eligibility") or []
        if not engineers:
            st.warning("No authorized, competent and available Plan Appraisal Engineer is currently eligible for this discipline.")
            return
        by_id = {str(x.get("user_id") or x.get("id")): x for x in engineers}
        selected = st.selectbox("Plan Appraisal Engineer", list(by_id), format_func=lambda x: by_id[x].get("full_name") or x, key=f"real_eng_{drawing_id}")
        if st.button("Assign / Reassign for Appraisal", type="primary", key=f"real_assign_eng_{drawing_id}"):
            if _safe(lambda: rpq.assign_engineer(drawing_id, selected), "Engineer assignment"):
                st.rerun()
        return

    if role == cfg.ROLE_ENGINEER and str(d.get("engineer_id") or "") == str(actor.get("id")) and status in {"assigned_engineer", "under_engineer_review", "review_resubmitted"}:
        st.info("The appraisal files uploaded here are bound to the current Designer revision and retained as controlled PSB records.")
        c1, c2 = st.columns(2)
        marked = c1.file_uploader("Marked-up / Appraised Drawing PDF", type=["pdf"], key=f"real_marked_{drawing_id}")
        report = c2.file_uploader("Design Appraisal Report PDF", type=["pdf"], key=f"real_report_{drawing_id}")
        decision = st.selectbox("Engineer technical decision", ["APPROVED", "APPROVED_AS_AMENDED", "INFORMATION", "REJECTED"], key=f"real_decision_{drawing_id}")
        note = st.text_area("Technical conclusion / rule references", key=f"real_eng_note_{drawing_id}")
        obs_desc = st.text_area("Observation / amendment (required for Approved as Amended or Rejected)", key=f"real_obs_{drawing_id}")
        clause = st.text_input("Rule / clause reference", key=f"real_clause_{drawing_id}")
        needs_surveyor = st.checkbox("Require Surveyor verification", key=f"real_surveyor_{drawing_id}")
        if st.button("Submit Controlled Appraisal", type="primary", key=f"real_submit_appraisal_{drawing_id}"):
            if marked is None or report is None or not note.strip():
                st.error("Both controlled appraisal PDFs and the technical conclusion are required.")
                return
            observations_payload = []
            if obs_desc.strip():
                observations_payload.append({"description": obs_desc.strip(), "severity": "Major", "clause_reference": clause.strip(), "drawing_reference": d.get("drawing_no")})
            if decision == "APPROVED_AS_AMENDED" and not observations_payload:
                st.error("Approved as Amended requires at least one recorded amendment.")
                return
            if decision == "REJECTED" and not observations_payload:
                st.error("Rejected requires at least one technical observation.")
                return
            ok1 = _safe(lambda: rpq.upload_engineer_artifact(drawing_id, "MARKED_UP_DRAWING", marked), "Marked-up drawing upload")
            if not ok1:
                return
            ok2 = _safe(lambda: rpq.upload_engineer_artifact(drawing_id, "APPRAISAL_REPORT", report), "Appraisal report upload")
            if not ok2:
                return
            if _safe(lambda: rpq.engineer_decision(drawing_id, decision, note.strip(), observations_payload, needs_surveyor), "Engineer decision"):
                st.success("Controlled appraisal package submitted.")
                st.rerun()
        return

    if role == cfg.ROLE_DESIGNER and str(d.get("designer_id") or "") == str(actor.get("id")) and status in {"designer_response", "rejected"}:
        st.warning("A corrected Designer revision is required. The existing revision remains immutable and will not be overwritten.")
        pdf = st.file_uploader(f"Corrected Designer PDF · Revision {int(d.get('current_revision') or 1)+1}", type=["pdf"], key=f"real_revision_{drawing_id}")
        note = st.text_area("Response to remarks / revision note", key=f"real_revision_note_{drawing_id}")
        if st.button("Submit Next Revision", type="primary", key=f"real_submit_revision_{drawing_id}"):
            if pdf is None or not note.strip():
                st.error("Corrected PDF and response note are required.")
            elif _safe(lambda: rpq.submit_revision(drawing_id, pdf, note.strip()), "Revision submission"):
                st.success("New controlled revision submitted. Previous revision retained in history.")
                st.rerun()
        return

    if role == cfg.ROLE_GM and status == "pending_gm_approval":
        note = st.text_area("GM decision note", key=f"real_gm_note_{drawing_id}")
        c1, c2 = st.columns(2)
        if c1.button("Approve", type="primary", key=f"real_gm_approve_{drawing_id}"):
            if _safe(lambda: rpq.gm_decision(drawing_id, "approved", note.strip()), "GM approval"):
                st.rerun()
        if c2.button("Return", key=f"real_gm_return_{drawing_id}"):
            if not note.strip():
                st.error("A return reason is required.")
            elif _safe(lambda: rpq.gm_decision(drawing_id, "returned", note.strip()), "GM return"):
                st.rerun()
        return

    st.info(f"Current status: {_label(status)}. Actions are available only to the authenticated role assigned to this drawing at this workflow stage.")
