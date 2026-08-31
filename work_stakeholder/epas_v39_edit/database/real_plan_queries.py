"""Production-only data service for the real Plan Appraisal workspace.

There is intentionally no demo fallback and no seeded data in this module.
All writes use authenticated SECURITY DEFINER RPCs and all files live in the
private `project-documents` Supabase Storage bucket.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from config.supabase_client import get_client
from database import production_queries as pq
from utils.file_validation import MAX_PDF_BYTES


def _db():
    client = get_client()
    if client is None:
        raise RuntimeError("Supabase is not configured. Real Plan Appraisal requires production Supabase.")
    return client


def register(project_id: str) -> list[dict]:
    return _db().rpc("epas_plan_appraisal_register_v42", {"p_project_id": project_id}).execute().data or []


def revision_package(drawing_id: str) -> list[dict]:
    return _db().rpc("epas_plan_revision_package_v42", {"p_drawing_id": drawing_id}).execute().data or []


def observations(drawing_id: str) -> list[dict]:
    return pq.plan_observations(drawing_id, open_only=False)


def events(drawing_id: str) -> list[dict]:
    return _db().table("workflow_events").select(
        "id,event_type,from_status,to_status,actor_id,note,metadata,created_at"
    ).eq("entity_type", "plan_drawing").eq("entity_id", drawing_id).order("created_at", desc=True).execute().data or []


def profile_name(user_id: str | None) -> str:
    if not user_id:
        return "System"
    rows = _db().table("profiles").select("full_name").eq("id", user_id).limit(1).execute().data or []
    return rows[0].get("full_name") or "User" if rows else "User"


def signed_storage_url(path: str, expires_in: int = 900) -> str:
    if not path:
        raise ValueError("Controlled file path is missing")
    signed = _db().storage.from_("project-documents").create_signed_url(path, expires_in)
    return signed.get("signedURL") or signed.get("signedUrl") or signed.get("url")


def submit_initial(project_id: str, drawing_no: str, title: str, discipline: str, uploaded_file: Any, note: str) -> dict:
    return pq.designer_submit_initial_drawing(project_id, drawing_no, title, discipline, uploaded_file, note)


def submit_revision(drawing_id: str, uploaded_file: Any, note: str) -> dict:
    return pq.designer_submit_revision_v15(drawing_id, uploaded_file, note)


def assign_manager(drawing_id: str, manager_id: str) -> dict:
    return pq.gm_assign_plan_manager(drawing_id, manager_id)


def assign_engineer(drawing_id: str, engineer_id: str) -> dict:
    return pq.dm_assign_engineer(drawing_id, engineer_id)


def eligible_engineers(project_id: str, discipline: str) -> list[dict]:
    # Production eligibility is authorization + competency + availability/workload.
    return pq.eligible("engineer", discipline)


def upload_engineer_artifact(drawing_id: str, artifact_type: str, uploaded_file: Any) -> dict:
    if artifact_type not in {"MARKED_UP_DRAWING", "APPRAISAL_REPORT"}:
        raise ValueError("Invalid controlled appraisal artifact type")
    return pq.engineer_register_appraisal_artifact(drawing_id, artifact_type, uploaded_file)


def engineer_decision(drawing_id: str, decision: str, note: str, observations_payload: list[dict], needs_surveyor_verification: bool = False) -> dict:
    if decision not in {"APPROVED", "APPROVED_AS_AMENDED", "INFORMATION", "REJECTED"}:
        raise ValueError("Invalid Engineer decision")
    return pq.engineer_submit_review_v21(drawing_id, decision, note, observations_payload, needs_surveyor_verification)


def manager_review(drawing_id: str, decision: str, note: str) -> dict:
    return pq.dm_review_plan(drawing_id, decision, note)


def gm_decision(drawing_id: str, decision: str, note: str) -> dict:
    return pq.gm_plan_decision(drawing_id, decision, note)


def project_members(project_id: str) -> list[dict]:
    return pq.members(project_id)
