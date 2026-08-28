"""Read/write adapter for EPAS demo mode.

It exposes the same callable names used by the active production query layer,
but serves a realistic in-memory dataset so the Streamlit UI works publicly
on port 8501 without Supabase.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Any
from config import demo_runtime


def _db():
    return demo_runtime._db()

def _uid():
    u = demo_runtime.current_user()
    return u.get("id") if u else None

def _profile_by_id(uid):
    return next((x for x in _db()["profiles"] if x.get("id") == uid), None)

def _project(project_id):
    return next((x for x in _db()["projects"] if x.get("id") == project_id), None)

def _vessel(project_id):
    return next((x for x in _db()["vessels"] if x.get("project_id") == project_id), None)

def _rfis(project_id=None):
    rows = _db()["rfis"]
    return [r for r in rows if project_id is None or r.get("project_id") == project_id]

def _obs(rfi_id=None, project_id=None):
    rows = _db()["observations"]
    if rfi_id:
        return [o for o in rows if o.get("rfi_id") == rfi_id]
    if project_id:
        ids = {r["id"] for r in _rfis(project_id)}
        return [o for o in rows if o.get("rfi_id") in ids]
    return rows

def _certs(project_id=None):
    rows = _db()["certificates"]
    return [c for c in rows if project_id is None or c.get("project_id") == project_id]

def _projects_for_user():
    user = demo_runtime.current_user() or {}
    role = user.get("role")
    uid = user.get("id")
    if role == "gm":
        return _db()["projects"]
    members = {x["project_id"] for x in _db()["team_assignments"] if x.get("user_id") == uid and x.get("role") == role}
    stakeholder = {x["project_id"] for x in _db()["stakeholders"] if x.get("contact_email") == user.get("email")}
    allowed = members | stakeholder
    # Preserve useful demo coverage for stakeholder roles.
    if not allowed and role in {"owner", "ship_management", "shipyard", "designer"}:
        st = next((x for x in _db()["stakeholders"] if x.get("stakeholder_type") == role), None)
        if st: allowed.add(st["project_id"])
    return [p for p in _db()["projects"] if p.get("id") in allowed]

def _tasks():
    role = (demo_runtime.current_user() or {}).get("role")
    projects = {p["id"] for p in _projects_for_user()}
    out=[]
    for r in _rfis():
        if r.get("project_id") not in projects: continue
        out.append({"id": r["id"], "project_id": r["project_id"], "task_type": "survey_rfi", "status": r.get("status"), "to_user_id": _uid(), "entity_id": r["id"], "note": r.get("survey_type"), "due_at": str(r.get("scheduled_date") or r.get("requested_date") or ""), "priority": r.get("priority","medium"), "created_at": str(r.get("created_at","")), "updated_at": str(r.get("created_at",""))})
    return out

def _project_health(pid):
    r = _rfis(pid); o = _obs(project_id=pid); c = _certs(pid)
    completed = sum(1 for x in r if x.get("status") in {"certificate_issued","closed"})
    pct = int(round((completed / max(len(r),1))*100))
    overdue = sum(1 for x in r if x.get("scheduled_date") and x.get("status") not in {"certificate_issued","closed"} and str(x.get("scheduled_date")) < str(date.today()))
    open_obs = sum(1 for x in o if x.get("status") == "open")
    phase = "In-Service Active" if any(str(p).endswith("in_service") for p in (_project(pid) or {}).get("phases", [])) else "Plan / NSC"
    cycle = 1 + sum(1 for x in r if x.get("phase") == "in_service" and x.get("status") in {"certificate_issued","closed"})
    future_dates = []
    for x in r:
        d = x.get("scheduled_date")
        if d:
            try:
                d_obj = d if isinstance(d, date) else date.fromisoformat(str(d))
                if d_obj >= date.today():
                    future_dates.append(d_obj)
            except Exception:
                continue
    next_due = min(future_dates).isoformat() if future_dates else ""
    return {"completion_pct": pct, "overdue_tasks": overdue, "open_observations": open_obs, "open_escalations": 0, "health_status": "Healthy" if pct >= 60 else "Watch", "current_phase": phase, "current_cycle": f"Cycle {cycle}", "next_survey_due": next_due, "certificate_count": len(c)}

def _stakeholder_registry_defaults():
    db = _db()
    rows = db.setdefault("stakeholder_registry", [])
    if not rows:
        defaults = [
            {"id": "demo-sr-owner-001", "stakeholder_type": "owner", "company_name": "Oceanic Vessel Holdings Ltd.", "registration_no": "OWN-001", "country": "Pakistan", "address": "Karachi", "city": "Karachi", "postal_code": "74000", "website": "https://example.com", "contact_name": "Ali Khan", "contact_designation": "Fleet Director", "contact_email": "owner@demo.epas", "contact_phone": "+92 21 1111111", "contact_mobile": "+92 300 1111111", "notes": "Demo owner", "status": "active"},
            {"id": "demo-sr-designer-001", "stakeholder_type": "designer", "company_name": "ABC Marine Design Ltd.", "registration_no": "DES-001", "country": "Pakistan", "address": "Lahore", "city": "Lahore", "postal_code": "54000", "website": "https://example.com", "contact_name": "Ahmed Raza", "contact_designation": "Naval Architect", "contact_email": "designer@demo.epas", "contact_phone": "+92 42 2222222", "contact_mobile": "+92 301 2222222", "notes": "Demo designer", "status": "active"},
            {"id": "demo-sr-sm-001", "stakeholder_type": "ship_management", "company_name": "Oceanic Ship Management Co.", "registration_no": "SM-001", "country": "Pakistan", "address": "Karachi", "city": "Karachi", "postal_code": "74000", "website": "https://example.com", "contact_name": "Salman Ali", "contact_designation": "Operations Manager", "contact_email": "shipmanagement@demo.epas", "contact_phone": "+92 21 3333333", "contact_mobile": "+92 302 3333333", "notes": "Demo ship management", "status": "active"},
            {"id": "demo-sr-yard-001", "stakeholder_type": "shipyard", "company_name": "Damen Shipyards", "registration_no": "YARD-001", "country": "Pakistan", "address": "Karachi", "city": "Karachi", "postal_code": "74000", "website": "https://example.com", "contact_name": "John Smith", "contact_designation": "Project Manager", "contact_email": "shipyard@demo.epas", "contact_phone": "+92 21 4444444", "contact_mobile": "+92 303 4444444", "notes": "Demo shipyard", "status": "active"},
        ]
        rows.extend(defaults)
    return rows

def _stakeholder_registry(type_=None):
    rows = _stakeholder_registry_defaults()
    return [r for r in rows if not type_ or r.get("stakeholder_type") == type_]

def _demo_read(name, *args, **kwargs):
    project_id = kwargs.get("project_id") or (args[0] if args and isinstance(args[0], str) and args[0] in {p["id"] for p in _db()["projects"]} else None)
    if name == "profile": return demo_runtime.current_user()
    if name == "users": return _db()["profiles"] if kwargs.get("role") is None else [x for x in _db()["profiles"] if x.get("role") == kwargs.get("role")]
    if name in {"stakeholder_registry", "stakeholder_registry_v414"}: return _stakeholder_registry(kwargs.get("stakeholder_type") or (args[0] if args else None))
    if name in {"projects", "authorized_projects_v36"}: return _projects_for_user()
    if name == "project": return _project(args[0])
    if name in {"vessel", "get_vessel_for_project"}: return _vessel(args[0])
    if name in {"members"}: return [x for x in _db()["team_assignments"] if x.get("project_id") == args[0]]
    if name in {"stakeholders"}: return [x for x in _db()["stakeholders"] if x.get("project_id") == args[0]]
    if name in {"rfis", "list_rfis"}: return _rfis(project_id)
    if name == "rfi": return next((x for x in _rfis() if x.get("id") == args[0]), None)
    if name in {"observations", "observations_for_project", "open_observations"}: return _obs(rfi_id=args[0] if name=="observations" and args else None, project_id=project_id if name!="observations" else None)
    if name in {"certificates", "list_certificates"}: return _certs(project_id)
    if name in {"ship_register_project", "ship_register_rows"}: return [_vessel(project_id)] if _vessel(project_id) else []
    if name in {"tasks", "all_project_tasks", "my_work_queue"}: return _tasks()
    if name in {"notifications"}: return []
    if name in {"metrics", "role_dashboard_summary", "role_dashboard_summary_v36"}:
        ps = _projects_for_user()
        tasks = _tasks()
        open_tasks = [t for t in tasks if t.get("status") in {"pending", "accepted", "in_progress"}]
        plan_pending = sum(1 for t in open_tasks if t.get("task_type") in {"GM_PLAN_FINAL_APPROVAL", "PLAN_APPRAISAL_GM_DESIGN_DECISION"})
        survey_pending = sum(1 for r in _rfis() if r.get("status") == "pending_gm_approval")
        return {
            "active_projects": len(ps),
            "open_observations": sum(_project_health(p["id"])["open_observations"] for p in ps),
            "survey_due": sum(1 for p in ps if _project_health(p["id"])["next_survey_due"]),
            "overdue_tasks": sum(_project_health(p["id"])["overdue_tasks"] for p in ps),
            "certificates": sum(_project_health(p["id"])["certificate_count"] for p in ps),
            "plan_pending_gm": plan_pending,
            "pending_decisions": survey_pending,
            "pending_gm_rfi": survey_pending,
            "open_tasks": len(open_tasks),
            "open_escalations": 0,
            "plan_total": 0,
            "role": (demo_runtime.current_user() or {}).get("role", ""),
        }
    if name in {"role_dashboard_detail", "project_health", "project_health_v15", "project_health_v36"}: return _project_health(args[0]) if args else {}
    if name in {"dashboard_project_health_bundle"}:
        pids = args[0] if args else []
        return {pid:_project_health(pid) for pid in pids}
    if name in {"project_phase_status", "project_phase_workflow_v36"}:
        phase_rows = []
        phases = [str(ph).lower() for ph in (_project(project_id) or {}).get("phases", [])]
        project_rfis = _rfis(project_id)
        terminal = {"certificate_issued", "closed", "completed", "accepted"}
        nsc_rfis = [row for row in project_rfis if row.get("phase") == "nsc_survey"]
        nsc_complete = bool(nsc_rfis) and all(row.get("status") in terminal for row in nsc_rfis)
        for phase in phases:
            if phase == "plan_appraisal":
                status = "completed"
            elif phase == "nsc_survey":
                status = "completed" if nsc_complete else "in_progress"
            elif phase == "in_service" and "nsc_survey" in phases and not nsc_complete:
                status = "locked"
            elif phase == "in_service":
                status = "in_progress"
            else:
                status = "ready"
            phase_rows.append({"phase": phase, "status": status})
        return phase_rows
    if name in {"stakeholder_fleet_bundle_v36", "stakeholder_fleet_summary"}:
        return [{"project_id":p["id"],"project_code":p.get("project_code"),"vessel":(_vessel(p["id"]) or {}).get("name"),"health":_project_health(p["id"])} for p in _projects_for_user()]
    if name in {"owner_fleet_bundle_v36", "ship_management_bundle_v36", "shipyard_nsc_bundle_v36"}: return {"projects": _projects_for_user(), "vessels": [_vessel(p["id"]) for p in _projects_for_user() if _vessel(p["id"])], "metrics": _demo_read("metrics")}
    if name in {"schedule_bundle_v36", "survey_control_tower", "survey_schedule_queue", "v36_lifecycle_cases", "project_timeline", "project_timeline_v35", "project_timeline_v36", "coordination_timeline_v36"}: return []
    if name == "plan_drawings":
        rows = _db().setdefault("plan_drawings", [])
        return [row for row in rows if not project_id or row.get("project_id") == project_id]
    if name in {"plan_drawings_by_ids", "plan_observations", "plan_observations_by_drawing_ids", "plan_revisions", "surveyor_plan_verification_queue", "survey_checklist", "survey_reports", "corrective_actions", "escalations", "milestones", "project_milestones", "risks", "decisions", "governance_register", "audit_events", "document_releases", "released_documents", "document_access_log", "list_documents", "designer_submission_queue", "ship_management_action_queue"}: return []
    if name in {"resource_workload", "resource_allocation_matrix", "sla_dashboard", "task_sla_snapshot", "security_preflight"}: return [] if name not in {"sla_dashboard"} else {"on_track":12,"due_soon":4,"overdue":2}
    if name == "global_search_v36": return []
    if name in {"vessel", "get_vessel_for_project"}: return _vessel(args[0])
    return []

def _demo_write(name, *args, **kwargs):
    if name == "designer_submit_initial_drawing":
        project_id, drawing_no, title, discipline, uploaded_file, note = args
        db = _db()
        rows = db.setdefault("plan_drawings", [])
        documents = db.setdefault("documents", [])
        revisions = db.setdefault("document_revisions", [])
        events = db.setdefault("plan_events", [])
        sequence = len(rows) + 1
        file_name = getattr(uploaded_file, "name", None) or f"{drawing_no}-REV-1.pdf"
        document_id = f"demo-plan-document-{sequence:03d}"
        drawing_id = f"demo-plan-{sequence:03d}"
        document = {
            "id": document_id, "project_id": project_id, "category": "drawing",
            "file_name": file_name, "version": 1, "status": "pending_review",
            "uploaded_by": _uid(), "uploaded_at": date.today(),
        }
        drawing = {
            "id": drawing_id, "project_id": project_id, "document_id": document_id,
            "drawing_no": drawing_no, "title": title, "discipline": discipline,
            "revision": 1, "current_revision": 1, "status": "submitted",
            "manager_id": None, "engineer_id": None, "designer_id": _uid(),
            "submitted_at": date.today(), "updated_at": date.today(),
            "current_file_name": file_name, "submission_note": note,
        }
        documents.append(document)
        rows.append(drawing)
        revisions.append({
            "id": f"demo-plan-revision-{sequence:03d}", "document_id": document_id,
            "revision": 1, "revision_no": 1, "status": "submitted",
            "file_name": file_name, "created_at": datetime.now().isoformat(),
            "submitted_at": datetime.now().isoformat(), "submitted_by": _uid(),
        })
        events.append({
            "id": f"demo-plan-event-{sequence:03d}", "drawing_id": drawing_id,
            "event_type": "SUBMITTED_TO_GM", "actor_id": _uid(), "note": note,
            "created_at": datetime.now().isoformat(),
        })
        return drawing
    if name == "stakeholder_create_rfi":
        project_id, vessel_id, phase, survey_type, requested_date, priority, scope_note = args
        rows = _db()["rfis"]
        sequence = len(rows) + 1
        new = {
            "id": f"demo-rfi-request-{sequence:03d}",
            "rfi_code": f"RFI-DEMO-{sequence:03d}",
            "project_id": project_id,
            "vessel_id": vessel_id,
            "phase": phase,
            "survey_type": survey_type,
            "status": "pending_allocation",
            "requested_date": requested_date,
            "scheduled_date": None,
            "requested_by": _uid(),
            "assigned_dm_id": None,
            "assigned_surveyor_id": None,
            "priority": priority,
            "scope_note": scope_note,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        rows.append(new)
        return new
    if name == "create_project":
        payload = kwargs.get("payload") or (args[0] if args else {})
        new = {"id": f"demo-{len(_db()['projects'])+1}", "project_code": payload.get("project_code", f"DEMO-{len(_db()['projects'])+1:03d}"), "name": payload.get("name","Demo Project"), "vessel_type": payload.get("vessel_type","Vessel"), "flag_state": payload.get("flag_state","Pakistan"), "phases": payload.get("phases", ["plan_appraisal","nsc_survey","in_service"]), "status":"active", "created_at":datetime.now().isoformat()}
        _db()["projects"].append(new)
        _db().setdefault("stakeholders", [])
        for item in payload.get("stakeholders", []) or []:
            reg = next((r for r in _stakeholder_registry() if r.get("id") == item.get("registry_id")), None)
            if reg:
                _db()["stakeholders"].append({
                    "id": f"demo-stakeholder-{len(_db()['stakeholders'])+1}",
                    "project_id": new["id"],
                    "registry_id": reg["id"],
                    "company_name": reg["company_name"],
                    "contact_name": reg.get("contact_name", ""),
                    "contact_email": reg.get("contact_email", ""),
                    "contact_phone": reg.get("contact_phone", ""),
                    "contact_designation": reg.get("contact_designation", ""),
                    "stakeholder_type": reg["stakeholder_type"],
                    "status": "active",
                })
        return new
    if name in {"create_stakeholder", "create_stakeholder_v414"}:
        payload = kwargs.get("payload") or (args[0] if args else {})
        rows = _stakeholder_registry_defaults()
        new = {"id": f"demo-sr-{len(rows)+1:03d}", "stakeholder_type": payload.get("stakeholder_type"), "company_name": payload.get("company_name"), "registration_no": payload.get("registration_no"), "country": payload.get("country"), "address": payload.get("address"), "city": payload.get("city"), "postal_code": payload.get("postal_code"), "website": payload.get("website"), "contact_name": payload.get("contact_name"), "contact_designation": payload.get("contact_designation"), "contact_email": payload.get("contact_email"), "contact_phone": payload.get("contact_phone"), "contact_mobile": payload.get("contact_mobile"), "notes": payload.get("notes"), "status": "active"}
        rows.append(new)
        return new
    return {"ok": True, "demo": True, "message": f"Demo action '{name}' completed in memory."}

def dispatch(name, *args, **kwargs):
    if name in {"create_project","stakeholder_create_rfi","dm_assign_engineer_v36","dm_assign_surveyor_v36","gm_decide_rfi","gm_handover_rfi","gm_plan_decision","gm_amended_design_decision","dm_review_plan","dm_forward_survey","dm_verify_corrective","dm_issue_corrective","assignee_submit_corrective_v36","designer_submit_initial_drawing","designer_submit_revision","engineer_submit_review_v36","engineer_register_appraisal_artifact","surveyor_verify_plan_appraisal","start_survey_execution_v36","submit_survey_report_v36","set_in_service_schedule_basis_v36","secure_accept_task","secure_start_task","secure_complete_task","complete_milestone","release_milestone","release_document","withdraw_document_release","close_project","issue_certificate","finalize_interim_certificate","create_scheduled_in_service_rfi","mark_all_notifications_read","mark_notification_read","refresh_task_sla","upload_certificate_pdf_v36","register_project_document","project_document_signed_url","certificate_pdf_signed_url","gm_add_risk","gm_record_decision","gm_escalation_decide_v36","dm_escalate","complete_survey_checklist_item","acknowledge_survey_scope","acknowledge_survey_drawing_package_v36","confirm_survey_execution_declaration","surveyor_accept_assignment_v36"}:
        return _demo_write(name,*args,**kwargs)
    return _demo_read(name,*args,**kwargs)

