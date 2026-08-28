"""EPAS Plan Appraisal Control Center.

Production intent:
Designer -> GM/Plan Appraisal Manager -> Authorized Engineer -> Review ->
Observations -> Designer Response -> Re-review -> Manager Review -> GM Approval.

The demo implementation uses the existing session database. The same state
transitions are mirrored by the upgrade_schema.sql tables for Supabase.
"""
from __future__ import annotations

import streamlit as st

from config import settings as cfg
from database import production_queries as q
from database import upgrade_queries as uq
from utils import helpers as h


def render(project: dict | None = None) -> None:
    if project is None:
        pid = st.session_state.get("selected_project_id")
        project = q.get_project(pid) if pid else None
    if not project:
        st.warning("No project selected.")
        return

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
        _render_group(intake, project, "No newly received plans are awaiting allocation.")
    with tabs[1]:
        _render_group(review, project, "No plans are currently in technical or manager review.")
    with tabs[2]:
        _revision_register(revisions, project)
    with tabs[3]:
        if not decisions:
            st.success("No plan decisions are currently waiting for GM action.")
        for d in decisions:
            if d["status"] == uq.PA_PENDING_GM:
                _gm_review_card(d, project)
            else:
                _gm_designer_correction_card(d, project)
    with tabs[4]:
        _render_group(approved, project, "No plans have received final GM approval yet.")


def _render_group(drawings: list[dict], project: dict, empty_message: str) -> None:
    if not drawings:
        st.info(empty_message)
        return
    drawing_tabs = st.tabs([
        f"{drawing['drawing_no']} · Rev {drawing['revision']}" for drawing in drawings
    ])
    for drawing_tab, drawing in zip(drawing_tabs, drawings):
        with drawing_tab:
            _drawing_card(drawing, project)


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


def _drawing_card(d: dict, project: dict) -> None:
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
            if d["status"] in (uq.PA_SUBMITTED, uq.PA_DESIGNER_RESPONSE):
                _manager_assignment(d, project)
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
            _pdf_download(d, "design drawing PDF", current, "Designer Drawing")
        with c2:
            design_file = f'{d["drawing_no"]}_Design-Calculations_Rev-{d["revision"]:02d}.pdf'
            st.caption(f"Design calculations / design report · Rev {d['revision']}")
            _pdf_download(d, "design report PDF", design_file, "Designer Design Report")
        st.caption(
            f'Also registered: {d["drawing_no"]}_Rule-Compliance_Rev-{d["revision"]:02d}.xlsx · '
            f'{d["drawing_no"]}_Transmittal_Rev-{d["revision"]:02d}.pdf'
        )

        appraised_statuses = {
            uq.PA_OBSERVATION_RAISED, uq.PA_DESIGNER_RESPONSE, uq.PA_REVIEW_RESUBMITTED,
            uq.PA_MANAGER_REVIEW, uq.PA_PENDING_GM, uq.PA_APPROVED, uq.PA_REJECTED,
        }
        if d["status"] in appraised_statuses:
            st.divider()
            st.markdown("**B · Files produced by PSB after appraisal**")
            c3, c4 = st.columns(2)
            with c3:
                appraised_file = f'{d["drawing_no"]}_Rev-{d["revision"]:02d}_PSB-Appraised-Drawing.pdf'
                st.caption("Appraised drawing PDF with review status and controlled revision")
                _pdf_download(d, "appraised drawing PDF", appraised_file, "PSB Appraised Drawing")
            with c4:
                report_file = f'{d["drawing_no"]}_Rev-{d["revision"]:02d}_Design-Appraisal-Report.pdf'
                st.caption("Design Appraisal Report PDF with findings, observations and recommendation")
                _pdf_download(d, "Design Appraisal Report PDF", report_file, "Design Appraisal Report")
        else:
            st.info("PSB appraisal PDFs will be created after the authorised engineer completes the technical appraisal.")


def _manager_assignment(d: dict, project: dict) -> None:
    dms = q.list_users(role=cfg.ROLE_DM)
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

