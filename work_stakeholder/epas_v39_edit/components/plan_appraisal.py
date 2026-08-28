"""EPAS Plan Appraisal Control Center.

Production intent:
Designer -> GM/Plan Appraisal Manager -> Authorized Engineer -> Review ->
Observations -> Designer Response -> Re-review -> Manager Review -> GM Approval.

The demo implementation uses the existing session database. The same state
transitions are mirrored by the upgrade_schema.sql tables for Supabase.
"""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from config import settings as cfg
from config.supabase_client import is_demo_mode
from database import production_queries as q
from database import upgrade_queries as uq
from utils import helpers as h


def render(project: dict | None = None, role: str | None = None) -> None:
    if project is None:
        pid = st.session_state.get("selected_project_id")
        project = q.get_project(pid) if pid else None
    if not project:
        st.warning("No project selected.")
        return
    role = role or q.profile().get("role", "readonly")

    st.markdown('<div class="section-title">Plan Appraisal</div>', unsafe_allow_html=True)
    st.caption(
        f"{project.get('project_code', 'Project')} · Controlled plan intake, allocation, "
        "technical review, revision control and GM approval."
    )

    with st.container(border=True):
        st.markdown("**Controlled appraisal route**")
        route = st.columns(6)
        for column, step in zip(route, [
            "1 · Designer submission", "2 · GM intake", "3 · DM allocation",
            "4 · Engineer review", "5 · Revision / response", "6 · GM decision",
        ]):
            column.caption(step)
        st.caption(
            "Every decision remains tied to the project, drawing number and revision. "
            "An accepted revision is locked; a conditional or returned decision creates a controlled instruction for follow-up."
        )

    if role in {"designer", "owner", "ship_management", "shipyard"}:
        _new_plan_submission(project, role)

    drawings = uq.list_plan_drawings(project["id"])
    _summary(drawings)
    st.write("")

    if not drawings:
        st.info("No plans have been received for this project. New Designer submissions will appear here automatically.")
        return

    intake_statuses = {uq.PA_SUBMITTED, uq.PA_ASSIGNED_MANAGER}
    review_statuses = {uq.PA_ASSIGNED_ENGINEER, uq.PA_UNDER_REVIEW, uq.PA_REVIEW_RESUBMITTED, uq.PA_MANAGER_REVIEW}
    revision_statuses = {uq.PA_OBSERVATION_RAISED, uq.PA_DESIGNER_RESPONSE, uq.PA_REVIEW_RESUBMITTED, uq.PA_REJECTED}
    decision_statuses = {uq.PA_PENDING_GM, uq.PA_REJECTED}

    intake = [d for d in drawings if d["status"] in intake_statuses]
    review = [d for d in drawings if d["status"] in review_statuses]
    revisions = [d for d in drawings if d["status"] in revision_statuses or uq.list_document_revisions(d["document_id"])]
    decisions = [d for d in drawings if d["status"] in decision_statuses]
    approved = [d for d in drawings if d["status"] == uq.PA_APPROVED]

    tabs = st.tabs([
        f"Received & Allocation ({len(intake)})",
        f"Technical Review ({len(review)})",
        f"Revisions & Observations ({len(revisions)})",
        f"GM Decisions ({len(decisions)})",
        f"Approved Plans ({len(approved)})",
    ])
    with tabs[0]:
        _render_group(intake, project, role, "No newly received plans are awaiting allocation.")
    with tabs[1]:
        _render_group(review, project, role, "No plans are currently in technical or manager review.")
    with tabs[2]:
        _revision_register(revisions, project)
    with tabs[3]:
        if not decisions:
            st.success("No plan decisions are currently waiting for GM action.")
        for d in decisions:
            if d["status"] == uq.PA_PENDING_GM and role == "gm":
                _gm_review_card(d, project)
            elif d["status"] == uq.PA_REJECTED and role == "gm":
                _gm_designer_correction_card(d, project)
            else:
                _drawing_card(d, project, role)
    with tabs[4]:
        _render_group(approved, project, role, "No plans have received final GM approval yet.")


def _render_group(drawings: list[dict], project: dict, role: str, empty_message: str) -> None:
    if not drawings:
        st.info(empty_message)
        return
    drawing_tabs = st.tabs([
        f"{drawing['drawing_no']} · Rev {drawing['revision']}" for drawing in drawings
    ])
    for drawing_tab, drawing in zip(drawing_tabs, drawings):
        with drawing_tab:
            _drawing_card(drawing, project, role)


def _revision_register(drawings: list[dict], project: dict) -> None:
    if not drawings:
        st.info("No revisions or plan observations have been recorded for this project.")
        return
    drawing_tabs = st.tabs([
        f"{drawing['drawing_no']} · Rev {drawing['revision']}" for drawing in drawings
    ])
    for drawing_tab, drawing in zip(drawing_tabs, drawings):
        with drawing_tab:
            st.markdown(
                f"**{drawing['drawing_no']} — {drawing['title']}** · Current revision "
                f"**{drawing['revision']}** · {uq.PA_STATUS_LABELS.get(drawing['status'], drawing['status'])}"
            )
            observations = uq.list_plan_observations(drawing["id"], open_only=False)
            open_count = sum(1 for item in observations if str(item.get("status", "open")).lower() == "open")
            c1, c2, c3 = st.columns(3)
            revisions = uq.list_document_revisions(drawing["document_id"])
            c1.metric("Recorded Revisions", len(revisions))
            c2.metric("Observations", len(observations))
            c3.metric("Open Observations", open_count)

            revision_tab, observation_tab, history_tab = st.tabs([
                "Revision Register", "Observations & Responses", "Workflow History"
            ])
            with revision_tab:
                if not revisions:
                    st.caption("Only the current plan revision is registered.")
                for revision in revisions:
                    st.markdown(
                        f"**Rev {revision.get('revision', '—')}** · "
                        f"{revision.get('status', '—')} · {revision.get('file_name', '—')}"
                    )
                    st.caption(str(revision.get("created_at") or ""))
            with observation_tab:
                if not observations:
                    st.success("No observations have been raised against this plan.")
                for observation in observations:
                    status = str(observation.get("status") or "open").replace("_", " ").title()
                    st.markdown(
                        f"**{observation.get('obs_code', 'Observation')}** · "
                        f"{observation.get('severity', '—')} · {status}"
                    )
                    st.caption(observation.get("description") or "No description recorded.")
                    response = observation.get("designer_response") or observation.get("response")
                    if response:
                        st.info(f"Designer response: {response}")
            with history_tab:
                events = uq.list_plan_events(drawing["id"])
                if not events:
                    st.caption("No workflow events have been recorded.")
                for event in events:
                    actor = q.get_user(event.get("actor_id"))
                    st.markdown(
                        f"**{event.get('event_type', 'Event').replace('_', ' ').title()}** · "
                        f"{actor['full_name'] if actor else 'System'}"
                    )
                    st.caption(f"{event.get('created_at', '')} · {event.get('note', '')}")


def _summary(drawings: list[dict]) -> None:
    total = len(drawings)
    approved = sum(d["status"] == uq.PA_APPROVED for d in drawings)
    observations = sum(len(uq.list_plan_observations(d["id"], open_only=True)) for d in drawings)
    pending = sum(d["status"] == uq.PA_PENDING_GM for d in drawings)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Drawings", total)
    c2.metric("Approved", approved)
    c3.metric("Open Observations", observations)
    c4.metric("Pending GM", pending)


def _drawing_card(d: dict, project: dict, role: str) -> None:
    with st.container(border=True):
        engineer = q.get_user(d.get("engineer_id"))
        manager = q.get_user(d.get("manager_id"))
        status_label = uq.PA_STATUS_LABELS.get(d["status"], d["status"])
        st.markdown(
            f'<div class="row-title-line"><span class="row-code">{d["drawing_no"]}</span>'
            f'<span class="row-vessel">{d["title"]}</span>'
            f'{h.badge(status_label, uq.status_badge_kind(d["status"]))}</div>'
            f'<div class="row-meta">Rev {d["revision"]} · {d["discipline"]} · '
            f'Manager: {manager["full_name"] if manager else "Unassigned"} · '
            f'Engineer: {engineer["full_name"] if engineer else "Unassigned"}</div>',
            unsafe_allow_html=True,
        )
        st.progress(uq.plan_progress(d["status"]))

        overview_tab, documents_tab, revisions_tab, correspondence_tab = st.tabs([
            "Drawing Overview", "Documents", "Revisions", "Correspondence & Workflow"
        ])
        with overview_tab:
            if role == "gm" and d["status"] == uq.PA_SUBMITTED:
                _manager_assignment(d, project)
            elif role == "dm" and d["status"] in {uq.PA_ASSIGNED_MANAGER, uq.PA_MANAGER_REVIEW}:
                _dm_plan_action(d, project)
            elif role == "engineer" and d["status"] in {
                uq.PA_ASSIGNED_ENGINEER, uq.PA_UNDER_REVIEW, uq.PA_REVIEW_RESUBMITTED,
                uq.PA_DESIGNER_RESPONSE,
            }:
                _engineer_plan_action(d)
            elif role == "designer" and d["status"] in {
                uq.PA_OBSERVATION_RAISED, uq.PA_REJECTED, uq.PA_DESIGNER_RESPONSE,
            }:
                _designer_revision_action(d)
            elif d["status"] in (uq.PA_ASSIGNED_ENGINEER, uq.PA_UNDER_REVIEW, uq.PA_REVIEW_RESUBMITTED):
                _resource_snapshot(d)
            elif d["status"] == uq.PA_OBSERVATION_RAISED:
                obs = uq.list_plan_observations(d["id"], open_only=True)
                for o in obs:
                    st.warning(f'{o["obs_code"]} · {o["severity"]}: {o["description"]}')
            elif d["status"] == uq.PA_MANAGER_REVIEW:
                st.info("Engineer review completed. Manager review is required before GM sign-off.")
            elif d["status"] == uq.PA_APPROVED:
                st.success("Approved drawing — current revision is locked.")

        with documents_tab:
            _document_package(d)

        with revisions_tab:
            for r in uq.list_document_revisions(d["document_id"]):
                current = " · **CURRENT**" if int(r["revision"]) == int(d["revision"]) else ""
                st.markdown(f'**Rev {r["revision"]}** · {r["status"]}{current}')
                st.caption(f'{r["file_name"]} · {r["created_at"]}')

        with correspondence_tab:
            observations = uq.list_plan_observations(d["id"], open_only=False)
            for observation in observations:
                st.markdown(
                    f'**{observation.get("obs_code", "Observation")}** · '
                    f'{observation.get("severity", "—")} · {str(observation.get("status", "open")).title()}'
                )
                st.caption(observation.get("description") or "No description recorded.")
                response = observation.get("designer_response") or observation.get("response")
                if response:
                    st.info(f"Designer response: {response}")
            events = uq.list_plan_events(d["id"])
            if not events and not observations:
                st.caption("No correspondence or workflow events have been recorded for this drawing.")
            for e in events:
                actor = q.get_user(e.get("actor_id"))
                st.markdown(f'**{str(e["event_type"]).replace("_", " ").title()}** · {actor["full_name"] if actor else "System"}')
                st.caption(f'{e["created_at"]} · {e.get("note", "")}')


def _demo_pdf(title: str, lines: list[str]) -> bytes:
    """Build a small valid PDF used only for downloadable demo documents."""
    def clean(value: str) -> str:
        return str(value).encode("latin-1", "replace").decode("latin-1").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    commands = ["BT", "/F1 16 Tf", "52 790 Td", f"({clean(title)}) Tj", "/F1 10 Tf"]
    for line in lines:
        commands.extend(["0 -24 Td", f"({clean(line)}) Tj"])
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >> endobj\n",
        f"4 0 obj << /Length {len(stream)} >> stream\n".encode("ascii") + stream + b"\nendstream endobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode("ascii"))
    return bytes(pdf)


def _pdf_download(d: dict, label: str, file_name: str, document_type: str) -> None:
    st.download_button(
        label=f"Download {label}",
        data=_demo_pdf(
            f"PSB - {document_type}",
            [
                f"Drawing: {d['drawing_no']} - {d['title']}",
                f"Revision: {d['revision']}",
                f"Discipline: {d['discipline']}",
                f"Workflow status: {uq.PA_STATUS_LABELS.get(d['status'], d['status'])}",
                "Demo controlled document generated by EPAS.",
            ],
        ),
        file_name=file_name,
        mime="application/pdf",
        key=f"pa_pdf_{document_type}_{d['id']}",
        use_container_width=True,
    )


def _document_package(d: dict) -> None:
    """Separate Designer source files from PSB appraisal deliverables."""
    with st.container(border=True):
        st.markdown("**Controlled PDF document package**")
        current = d.get("current_file_name") or f'{d.get("drawing_no", "Plan")}_Rev-{d.get("revision", 1):02d}.pdf'
        st.markdown("**A · Files received from Designer**")
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"Design drawing PDF · Rev {d['revision']}")
            if is_demo_mode():
                _pdf_download(d, "design drawing PDF", current, "Designer Drawing")
            else:
                try:
                    st.link_button("Open design drawing PDF", q.project_document_signed_url(d["document_id"]), use_container_width=True)
                except Exception:
                    st.warning("The controlled drawing file is not available to this role.")
        with c2:
            design_file = f'{d["drawing_no"]}_Design-Calculations_Rev-{d["revision"]:02d}.pdf'
            st.caption(f"Design calculations / design report · Rev {d['revision']}")
            if is_demo_mode():
                _pdf_download(d, "design report PDF", design_file, "Designer Design Report")
            else:
                st.info("Design report is registered with the project document package when supplied.")
        st.caption(
            f'Also registered: {d["drawing_no"]}_Rule-Compliance_Rev-{d["revision"]:02d}.xlsx · '
            f'{d["drawing_no"]}_Transmittal_Rev-{d["revision"]:02d}.pdf'
        )

        appraised_statuses = {
            uq.PA_OBSERVATION_RAISED, uq.PA_DESIGNER_RESPONSE, uq.PA_REVIEW_RESUBMITTED,
            uq.PA_MANAGER_REVIEW, uq.PA_PENDING_GM, uq.PA_APPROVED, uq.PA_REJECTED,
        }
        artifacts = uq.list_appraisal_artifacts(d["id"])
        if d["status"] in appraised_statuses:
            st.divider()
            st.markdown("**B · Files produced by PSB after appraisal**")
            c3, c4 = st.columns(2)
            with c3:
                st.caption("Appraised drawing PDF with review status and controlled revision")
                artifact = next((x for x in artifacts if x.get("artifact_type") == "appraised_drawing"), None)
                if artifact and not is_demo_mode():
                    st.link_button("Open PSB appraised drawing PDF", q.project_storage_signed_url(artifact["storage_path"]), use_container_width=True)
                elif artifact:
                    _pdf_download(d, "appraised drawing PDF", artifact["file_name"], "PSB Appraised Drawing")
                else:
                    st.warning("Awaiting engineer-uploaded appraised drawing PDF.")
            with c4:
                st.caption("Design Appraisal Report PDF with findings, observations and recommendation")
                artifact = next((x for x in artifacts if x.get("artifact_type") == "appraisal_report"), None)
                if artifact and not is_demo_mode():
                    st.link_button("Open Design Appraisal Report PDF", q.project_storage_signed_url(artifact["storage_path"]), use_container_width=True)
                elif artifact:
                    _pdf_download(d, "Design Appraisal Report PDF", artifact["file_name"], "Design Appraisal Report")
                else:
                    st.warning("Awaiting engineer-uploaded Design Appraisal Report PDF.")
        else:
            st.info("PSB appraisal PDFs will be created after the authorised engineer completes the technical appraisal.")


def _new_plan_submission(project: dict, role: str) -> None:
    """Project-bound intake available to the authorised submitting stakeholder."""
    with st.expander("Submit a new design plan to this project", expanded=False):
        st.caption("The initial PDF becomes Revision 1 and is routed to GM intake for this project only.")
        c1, c2 = st.columns(2)
        drawing_no = c1.text_input("Drawing number", key=f"pa_new_no_{project['id']}_{role}")
        title = c2.text_input("Drawing title", key=f"pa_new_title_{project['id']}_{role}")
        discipline = st.selectbox(
            "Discipline", ["Hull & Structure", "Stability", "Machinery", "Electrical", "Fire Safety"],
            key=f"pa_new_disc_{project['id']}_{role}",
        )
        drawing_pdf = st.file_uploader(
            "Design drawing PDF · Revision 1", type=["pdf"],
            key=f"pa_new_pdf_{project['id']}_{role}",
        )
        note = st.text_area(
            "Designer transmittal / scope note", key=f"pa_new_note_{project['id']}_{role}",
        )
        if st.button("Submit plan to GM intake", type="primary", key=f"pa_new_submit_{project['id']}_{role}"):
            if not drawing_no.strip() or not title.strip() or not note.strip() or drawing_pdf is None:
                st.error("Drawing number, title, PDF and transmittal note are required.")
            else:
                try:
                    actor = q.profile()
                    uq.submit_initial_plan(
                        project["id"], drawing_no, title, discipline, drawing_pdf, note, actor["id"]
                    )
                    st.success("Revision 1 was registered in this project and sent to GM intake.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Plan submission could not be completed: {exc}")


def _dm_plan_action(d: dict, project: dict) -> None:
    actor = q.profile()
    if d.get("manager_id") and d.get("manager_id") != actor.get("id"):
        st.info("This appraisal is assigned to another Department Manager. You have review-only access.")
        return
    if d["status"] == uq.PA_ASSIGNED_MANAGER:
        engineers = uq.eligible_engineers(d["discipline"])
        if not engineers:
            st.error("No authorised, competent and available engineer is eligible for this discipline.")
            return
        engineer_ids = [item["id"] for item in engineers]
        selected = st.selectbox(
            "Assign authorised engineer", engineer_ids,
            format_func=lambda user_id: q.get_user(user_id)["full_name"],
            key=f"pa_dm_engineer_{d['id']}",
        )
        if st.button("Assign for technical appraisal", type="primary", key=f"pa_dm_assign_{d['id']}"):
            uq.assign_engineer(d["id"], selected, actor["id"])
            st.rerun()
        return

    st.markdown("**DM appraisal review**")
    decision = st.selectbox(
        "Manager decision",
        ["Appraisal Approved", "Appraisal Requires Changes", "Design Rejected / Amended"],
        key=f"pa_dm_decision_{d['id']}",
    )
    note = st.text_area("Manager review note", key=f"pa_dm_note_{d['id']}")
    if st.button("Record DM decision", type="primary", key=f"pa_dm_record_{d['id']}"):
        if not note.strip():
            st.error("A controlled manager review note is required.")
        else:
            uq.manager_review_decision(d["id"], actor["id"], decision, note)
            st.rerun()


def _engineer_plan_action(d: dict) -> None:
    actor = q.profile()
    if d.get("engineer_id") != actor.get("id"):
        st.info("This drawing is assigned to another engineer. You have review-only access.")
        return
    if d["status"] == uq.PA_ASSIGNED_ENGINEER:
        if st.button("Start technical appraisal", type="primary", key=f"pa_eng_start_{d['id']}"):
            uq.start_engineer_review(d["id"], actor["id"])
            st.rerun()
        return
    note = st.text_area(
        "Technical appraisal findings / rule references", key=f"pa_eng_note_{d['id']}",
    )
    cfile1, cfile2 = st.columns(2)
    appraised_pdf = cfile1.file_uploader(
        "PSB appraised drawing PDF", type=["pdf"], key=f"pa_eng_drawing_pdf_{d['id']}"
    )
    report_pdf = cfile2.file_uploader(
        "Design Appraisal Report PDF", type=["pdf"], key=f"pa_eng_report_pdf_{d['id']}"
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Complete appraisal · Recommend acceptance", type="primary", key=f"pa_eng_accept_{d['id']}"):
            if not note.strip() or appraised_pdf is None or report_pdf is None:
                st.error("Findings, appraised drawing PDF and Design Appraisal Report PDF are required.")
            else:
                uq.register_appraisal_artifact(d["id"], "appraised_drawing", appraised_pdf, actor["id"])
                uq.register_appraisal_artifact(d["id"], "appraisal_report", report_pdf, actor["id"])
                uq.engineer_complete_review(d["id"], actor["id"], True, note)
                st.rerun()
    with c2:
        if st.button("Raise observation / correction", key=f"pa_eng_obs_{d['id']}"):
            if not note.strip() or appraised_pdf is None or report_pdf is None:
                st.error("Correction details and both controlled appraisal PDFs are required.")
            else:
                uq.register_appraisal_artifact(d["id"], "appraised_drawing", appraised_pdf, actor["id"])
                uq.register_appraisal_artifact(d["id"], "appraisal_report", report_pdf, actor["id"])
                uq.engineer_complete_review(d["id"], actor["id"], False, note)
                st.rerun()


def _designer_revision_action(d: dict) -> None:
    actor = q.profile()
    if d.get("designer_id") != actor.get("id"):
        st.info("Only the submitting Designer can upload the next revision.")
        return
    observations = uq.list_plan_observations(d["id"], open_only=True)
    for observation in observations:
        st.warning(f'{observation["obs_code"]} · {observation["severity"]}: {observation["description"]}')
    response = st.text_area("Designer response / correction summary", key=f"pa_des_response_{d['id']}")
    revision_pdf = st.file_uploader(
        f"Revised design drawing PDF · next revision after Rev {d['revision']}", type=["pdf"],
        key=f"pa_des_revision_{d['id']}",
    )
    if st.button("Submit revised drawing for re-appraisal", type="primary", key=f"pa_des_submit_{d['id']}"):
        if not response.strip() or revision_pdf is None:
            st.error("A response and revised PDF are required.")
        else:
            if observations:
                uq.designer_respond(d["id"], actor["id"], response)
            else:
                uq.designer_amendment_response(d["id"], actor["id"], response)
            uq.resubmit_for_engineer_review(d["id"], actor["id"], revision_pdf)
            st.rerun()


def _manager_assignment(d: dict, project: dict) -> None:
    # Use the production query's canonical API directly.  The older
    # ``list_users`` compatibility name is not available on every deployed
    # Streamlit worker during rolling upgrades.
    dms = q.users(role=cfg.ROLE_DM)
    eligible = [u for u in dms if uq.is_project_manager_eligible(project["id"], u["id"])]
    if not eligible:
        st.error("No eligible Plan Appraisal Manager is available for this project.")
        return
    options = [u["id"] for u in eligible]
    selected = st.selectbox("Plan Appraisal Manager", options, format_func=lambda x: q.get_user(x)["full_name"], key=f"pa_mgr_{d['id']}")
    if st.button("Hand over to Manager →", key=f"pa_handover_{d['id']}", type="primary"):
        uq.assign_plan_manager(d["id"], selected, q.current_gm()["id"])
        st.toast("Plan appraisal handed over to the manager.", icon="📨")
        st.rerun()


def _resource_snapshot(d: dict) -> None:
    engineer = q.get_user(d.get("engineer_id"))
    if engineer:
        check = uq.engineer_eligibility(engineer["id"], d["discipline"])
        st.markdown(f'**Assigned engineer:** {engineer["full_name"]}')
        st.caption(" · ".join(check["reasons"]))


def _gm_review_card(d: dict, project: dict) -> None:
    with st.container(border=True):
        st.markdown(f'**{d["drawing_no"]} — {d["title"]}** · Rev {d["revision"]}')
        st.write(f'Discipline: **{d["discipline"]}**')
        st.success("Manager has completed review and forwarded this drawing to GM.")
        _document_package(d)
        obs = uq.list_plan_observations(d["id"], open_only=True)
        if obs:
            st.warning(f"{len(obs)} open observation(s) remain.")
            for o in obs:
                st.markdown(f'- **{o["obs_code"]}** · {o["severity"]}: {o["description"]}')
        note = st.text_area("GM decision / Designer instruction", key=f"gm_pa_note_{d['id']}")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("Accept", key=f"gm_pa_approve_{d['id']}", type="primary", use_container_width=True):
                uq.gm_plan_decision(d["id"], "approved", note, q.current_gm()["id"])
                st.rerun()
        with c2:
            if st.button("Accept with conditions", key=f"gm_pa_conditional_{d['id']}", use_container_width=True):
                if not note.strip():
                    st.error("Record the conditions before accepting.")
                else:
                    uq.gm_plan_decision(d["id"], "approved", f"CONDITIONAL ACCEPTANCE: {note}", q.current_gm()["id"])
                    st.rerun()
        with c3:
            if st.button("Send to Designer", key=f"gm_pa_designer_{d['id']}", use_container_width=True):
                if not note.strip():
                    st.error("Add the Designer correction instruction.")
                else:
                    uq.gm_send_to_designer(d["id"], q.current_gm()["id"], note)
                    st.rerun()
        with c4:
            if st.button("Return to DM", key=f"gm_pa_return_{d['id']}", use_container_width=True):
                if not note.strip():
                    st.error("Add a reason before returning.")
                else:
                    uq.gm_plan_decision(d["id"], "returned", note, q.current_gm()["id"])
                    st.rerun()


def _gm_designer_correction_card(d: dict, project: dict) -> None:
    with st.container(border=True):
        st.markdown(f'**{d["drawing_no"]} — {d["title"]}** · Rev {d["revision"]}')
        st.warning("Manager marked the design as rejected / amended. GM must send it to the Designer for correction.")
        note = st.text_area("GM instruction to Designer", key=f"gm_designer_note_{d["id"]}")
        if st.button("Send to Designer for Correction →", key=f"gm_to_designer_{d["id"]}", type="primary"):
            if not note.strip():
                st.error("Enter the correction instruction before sending.")
            else:
                uq.gm_send_to_designer(d["id"], q.current_gm()["id"], note)
                st.rerun()

