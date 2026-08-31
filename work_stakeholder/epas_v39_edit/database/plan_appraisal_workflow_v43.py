"""PSB EPAS v4.3 Plan Appraisal workflow service.

Exact route:
Designer -> GM intake -> Plan Appraisal Manager -> Plan Appraisal Engineer ->
Plan Appraisal Manager review -> GM final decision -> Designer delivery.

Only Designer and Plan Appraisal Engineer upload technical files. GM and Manager
route/review only. All state changes use the existing authenticated SECURITY
DEFINER production RPCs; this service adds strict role/assignment validation and
maps user-facing actions to the production decision vocabulary.
"""
from __future__ import annotations

from typing import Any

from config import settings as cfg
from database import production_queries as pq
from database import real_plan_queries as rpq

ENGINEER_RESULTS = {
    "APPROVED",
    "APPROVED_AS_AMENDED",
    "INFORMATION",
    "REJECTED",
}


def actor() -> dict:
    return pq.profile()


def _require_role(role: str) -> dict:
    me = actor()
    if me.get("role") != role:
        raise PermissionError(f"This action requires role: {role}")
    return me


def _drawing(drawing_id: str) -> dict:
    row = pq.plan_drawing(drawing_id)
    if not row:
        raise ValueError("Plan drawing not found")
    return row


def submit_initial(project_id: str, drawing_no: str, title: str, discipline: str, pdf: Any, note: str) -> dict:
    _require_role(cfg.ROLE_DESIGNER)
    if not drawing_no.strip() or not title.strip() or not note.strip() or pdf is None:
        raise ValueError("Drawing number, title, PDF and submission note are required")
    return rpq.submit_initial(project_id, drawing_no.strip(), title.strip(), discipline, pdf, note.strip())


def submit_revision(drawing_id: str, pdf: Any, note: str) -> dict:
    me = _require_role(cfg.ROLE_DESIGNER)
    d = _drawing(drawing_id)
    if str(d.get("designer_id") or "") != str(me.get("id")):
        raise PermissionError("This drawing belongs to another Designer")
    if d.get("status") not in {"designer_response", "rejected"}:
        raise ValueError("A new revision is not requested at the current workflow stage")
    if pdf is None or not note.strip():
        raise ValueError("Revised drawing PDF and revision note are required")
    return rpq.submit_revision(drawing_id, pdf, note.strip())


def gm_route_to_manager(drawing_id: str, manager_id: str) -> dict:
    _require_role(cfg.ROLE_GM)
    d = _drawing(drawing_id)
    if d.get("status") != "submitted":
        raise ValueError("Only newly received Designer submissions can be routed by GM")
    if not manager_id:
        raise ValueError("Plan Appraisal Manager is required")
    return rpq.assign_manager(drawing_id, manager_id)


def manager_route_to_engineer(drawing_id: str, engineer_id: str) -> dict:
    me = _require_role(cfg.ROLE_DM)
    d = _drawing(drawing_id)
    if str(d.get("manager_id") or "") != str(me.get("id")):
        raise PermissionError("This drawing is assigned to another Plan Appraisal Manager")
    if d.get("status") not in {"assigned_manager", "revision_pending_dm"}:
        raise ValueError("Drawing is not awaiting Engineer allocation")
    if not engineer_id:
        raise ValueError("Plan Appraisal Engineer is required")
    return rpq.assign_engineer(drawing_id, engineer_id)


def eligible_engineers(project_id: str, discipline: str) -> list[dict]:
    return rpq.eligible_engineers(project_id, discipline)


def engineer_submit_appraisal(
    drawing_id: str,
    result: str,
    appraisal_note: str,
    remark_text: str,
    marked_pdf: Any | None = None,
    appraisal_pdf: Any | None = None,
) -> dict:
    me = _require_role(cfg.ROLE_ENGINEER)
    d = _drawing(drawing_id)
    if str(d.get("engineer_id") or "") != str(me.get("id")):
        raise PermissionError("This drawing is assigned to another Plan Appraisal Engineer")
    if d.get("status") not in {"assigned_engineer", "under_engineer_review", "review_resubmitted"}:
        raise ValueError("Drawing is not at Engineer appraisal stage")
    if result not in ENGINEER_RESULTS:
        raise ValueError("Invalid appraisal result")
    if not appraisal_note.strip():
        raise ValueError("Appraisal note is required")
    if marked_pdf is None and appraisal_pdf is None:
        raise ValueError("Attach at least one PSB appraisal PDF")
    if result in {"APPROVED_AS_AMENDED", "REJECTED"} and not remark_text.strip():
        raise ValueError("This appraisal result requires a technical remark")

    if marked_pdf is not None:
        rpq.upload_engineer_artifact(drawing_id, "MARKED_UP_DRAWING", marked_pdf)
    if appraisal_pdf is not None:
        rpq.upload_engineer_artifact(drawing_id, "APPRAISAL_REPORT", appraisal_pdf)

    observations = []
    if remark_text.strip():
        observations.append({
            "description": remark_text.strip(),
            "severity": "Major",
            "drawing_reference": d.get("drawing_no"),
        })
    return rpq.engineer_decision(
        drawing_id,
        result,
        appraisal_note.strip(),
        observations,
        False,
    )


def manager_review(drawing_id: str, action: str, note: str) -> dict:
    me = _require_role(cfg.ROLE_DM)
    d = _drawing(drawing_id)
    if str(d.get("manager_id") or "") != str(me.get("id")):
        raise PermissionError("This drawing is assigned to another Plan Appraisal Manager")
    if d.get("status") != "manager_review":
        raise ValueError("Drawing is not awaiting Manager review")
    mapping = {
        "FORWARD_TO_GM": "approved",
        "RETURN_TO_ENGINEER": "changes_required",
        "SEND_TO_GM_FOR_DESIGNER_RETURN": "rejected_amended",
    }
    if action not in mapping:
        raise ValueError("Invalid Manager review action")
    if action != "FORWARD_TO_GM" and not note.strip():
        raise ValueError("A reason is required when returning or escalating")
    return rpq.manager_review(drawing_id, mapping[action], note.strip())


def gm_final_decision(drawing_id: str, action: str, note: str) -> dict:
    _require_role(cfg.ROLE_GM)
    d = _drawing(drawing_id)
    if d.get("status") != "pending_gm_approval":
        raise ValueError("Drawing is not awaiting GM final decision")
    mapping = {
        "APPROVE_AND_DELIVER": "approved",
        "RETURN_TO_DESIGNER": "send_to_designer",
    }
    if action not in mapping:
        raise ValueError("Invalid GM decision")
    if action == "RETURN_TO_DESIGNER" and not note.strip():
        raise ValueError("Return to Designer requires a reason")
    return rpq.gm_decision(drawing_id, mapping[action], note.strip())


def managers_for_project(project_id: str) -> list[dict]:
    rows = rpq.project_members(project_id)
    managers: list[dict] = []
    for row in rows:
        profile = row.get("profiles") or row.get("profile") or {}
        role = row.get("role") or profile.get("role")
        if role == cfg.ROLE_DM and profile.get("id"):
            managers.append(profile)
    return managers


def package(drawing_id: str) -> list[dict]:
    return rpq.revision_package(drawing_id)


def remarks(drawing_id: str) -> list[dict]:
    return rpq.observations(drawing_id)


def events(drawing_id: str) -> list[dict]:
    return rpq.events(drawing_id)


def signed_url(path: str) -> str:
    return rpq.signed_storage_url(path)


def delivered_to_designer(drawing: dict) -> bool:
    # Approved artifacts are immediately visible to the drawing's Designer under
    # the v4.2 project/RLS policy. This is the controlled in-system delivery state.
    return drawing.get("status") == "approved"
