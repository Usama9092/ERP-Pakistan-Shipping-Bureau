"""PSB Plan Appraisal v4.2 · professional production UI.

Visual treatment follows mature classification-society electronic plan approval
patterns: dense register at left, controlled drawing dossier at right, prominent
revision/status visibility, document lineage and restrained maritime styling.
All data and actions remain production Supabase-backed through real_plan_queries.
"""
from __future__ import annotations

import html
from collections import defaultdict

import streamlit as st

from config import settings as cfg
from config.supabase_client import is_demo_mode
from database import production_queries as pq
from database import real_plan_queries as rpq
from components.plan_appraisal_real import _workflow_action, _designer_new_plan

STATUS_LABELS = {
    "submitted": "Submitted",
    "assigned_manager": "Manager Assigned",
    "assigned_engineer": "Engineer Assigned",
    "under_engineer_review": "Engineer Review",
    "observation_raised": "Remarks Issued",
    "designer_response": "Designer Response",
    "revision_pending_dm": "Revision Review",
    "review_resubmitted": "Re-appraisal",
    "manager_review": "Manager Review",
    "surveyor_verification_pending": "Surveyor Verification",
    "pending_gm_approval": "Pending GM",
    "approved": "Approved",
    "rejected": "Returned",
}

STEPS = [
    ("submitted", "Received"),
    ("assigned_manager", "Allocated"),
    ("assigned_engineer", "Engineer"),
    ("under_engineer_review", "Appraisal"),
    ("manager_review", "Manager"),
    ("pending_gm_approval", "GM Decision"),
    ("approved", "Approved"),
]


def _esc(value) -> str:
    return html.escape(str(value if value not in (None, "") else "—"))


def _label(status) -> str:
    return STATUS_LABELS.get(str(status or ""), str(status or "—").replace("_", " ").title())


def _tone(status: str) -> str:
    if status == "approved": return "good"
    if status in {"rejected", "designer_response", "observation_raised"}: return "warn"
    if status in {"pending_gm_approval", "manager_review"}: return "attention"
    return "active"


def _safe(fn, label: str):
    try:
        return fn()
    except Exception as exc:
        st.error(f"{label} could not be loaded: {exc}")
        return None


def _css() -> None:
    st.markdown("""
    <style>
    .pa-shell{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
    .pa-hero{background:linear-gradient(135deg,#06253b 0%,#0b3c59 62%,#0d5970 100%);border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:24px 26px;color:white;box-shadow:0 14px 34px rgba(4,31,49,.16);margin-bottom:14px;position:relative;overflow:hidden}
    .pa-hero:after{content:"";position:absolute;right:-70px;top:-90px;width:260px;height:260px;border-radius:50%;border:42px solid rgba(255,255,255,.045)}
    .pa-eyebrow{font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#8dd8e7;margin-bottom:6px}
    .pa-title{font-size:28px;line-height:1.05;font-weight:760;letter-spacing:-.02em;margin:0 0 7px}
    .pa-sub{font-size:13px;color:#c9dce5;max-width:820px}
    .pa-secure{display:inline-flex;align-items:center;gap:7px;margin-top:13px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:6px 10px;font-size:11px;color:#eaf6f8}
    .pa-kpis{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:12px 0 18px}
    .pa-kpi{background:#fff;border:1px solid #dfe7ec;border-radius:13px;padding:13px 15px;box-shadow:0 3px 12px rgba(14,47,68,.045)}
    .pa-kpi .v{font-size:22px;font-weight:760;color:#102f43;line-height:1.1}.pa-kpi .l{font-size:10px;font-weight:760;color:#748895;letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
    .pa-section-label{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#627b8a;margin:3px 0 8px}
    .pa-register-head{display:flex;align-items:flex-end;justify-content:space-between;margin:0 0 8px}.pa-register-head h3{margin:0;color:#16384d;font-size:18px}.pa-register-head span{font-size:11px;color:#758b98}
    .pa-disc{font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#5d7481;padding:8px 2px 5px}
    .pa-row{border:1px solid #e1e8ec;border-radius:11px;padding:10px 11px;margin:0 0 7px;background:#fff;transition:.15s ease}.pa-row.sel{border-color:#2a8ca2;box-shadow:0 0 0 2px rgba(42,140,162,.09);background:#f8fcfd}
    .pa-row-top{display:flex;align-items:center;gap:7px;margin-bottom:4px}.pa-code{font-size:12px;font-weight:800;color:#113b54}.pa-rev{font-size:10px;font-weight:800;color:#54707f;background:#edf3f6;border-radius:6px;padding:2px 6px}.pa-row-title{font-size:12px;color:#293f4d;line-height:1.35}.pa-row-meta{font-size:10px;color:#7c909a;margin-top:5px}
    .pa-pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 8px;font-size:9px;font-weight:850;letter-spacing:.035em;text-transform:uppercase;border:1px solid transparent}.pa-pill.good{color:#17734f;background:#e8f6ef;border-color:#c8e9d9}.pa-pill.warn{color:#9a5615;background:#fff4df;border-color:#f2dfb7}.pa-pill.attention{color:#765a09;background:#fff9d9;border-color:#eee39b}.pa-pill.active{color:#13637b;background:#e9f6f9;border-color:#c8e8ef}
    .pa-dossier{border:1px solid #dbe5ea;border-radius:16px;background:#fff;box-shadow:0 8px 26px rgba(18,54,75,.06);overflow:hidden;margin-bottom:12px}.pa-dossier-head{padding:18px 20px;border-bottom:1px solid #e5ecef;background:linear-gradient(180deg,#fff,#fbfdfe)}
    .pa-docline{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.pa-docno{font-size:13px;font-weight:850;color:#0e5870;letter-spacing:.035em}.pa-doctitle{font-size:21px;font-weight:760;color:#15384d;letter-spacing:-.01em}.pa-dossier-meta{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;color:#6b818d;font-size:11px}.pa-dossier-meta b{color:#334e5e}
    .pa-people{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:12px 20px 16px}.pa-person{border:1px solid #e4eaee;border-radius:10px;padding:9px 10px;background:#fbfcfd}.pa-person span{display:block;font-size:9px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#80919b}.pa-person strong{display:block;font-size:12px;color:#263f4e;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .pa-stepper{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:5px;margin:5px 0 14px}.pa-step{position:relative;text-align:center}.pa-step:before{content:"";display:block;height:4px;background:#e1e8ec;border-radius:9px;margin-bottom:5px}.pa-step.done:before{background:#2f879b}.pa-step.current:before{background:#d59b27}.pa-step span{font-size:9px;color:#768b96;font-weight:700}.pa-step.current span{color:#765a09}.pa-step.done span{color:#245e70}
    .pa-rev-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}.pa-rev-title{font-size:15px;font-weight:800;color:#193b4f}.pa-current{font-size:9px;font-weight:850;letter-spacing:.06em;color:#16664b;background:#e8f6ef;border:1px solid #c8e9d9;border-radius:999px;padding:3px 7px}
    .pa-filebox{border:1px solid #e3e9ed;border-radius:11px;padding:11px;background:#fbfcfd;min-height:108px}.pa-filebox .kind{font-size:9px;font-weight:850;color:#6a808c;letter-spacing:.08em;text-transform:uppercase}.pa-filebox .name{font-size:12px;font-weight:700;color:#263f4d;margin:5px 0}.pa-filebox .meta{font-size:9px;color:#87969e;line-height:1.45}
    .pa-remark{border-left:3px solid #d9a039;border-radius:8px;background:#fffaf0;padding:11px 13px;margin-bottom:8px}.pa-remark.resolved{border-left-color:#4a9b78;background:#f5fbf8}.pa-remark h4{font-size:12px;margin:0;color:#3d4f59}.pa-remark p{font-size:12px;margin:6px 0;color:#475b65}.pa-remark small{color:#7c8e96}
    .pa-event{display:grid;grid-template-columns:18px 1fr;gap:9px;padding:8px 0;border-bottom:1px solid #edf1f3}.pa-event:last-child{border-bottom:0}.pa-dot{width:9px;height:9px;margin-top:4px;border-radius:50%;background:#3a8ea1;box-shadow:0 0 0 4px #e9f5f7}.pa-event b{font-size:11px;color:#2e4654}.pa-event div div{font-size:10px;color:#7b8e98;margin-top:2px}
    div[data-testid="stTabs"] button[role="tab"]{font-size:12px;font-weight:700;color:#536d7a;padding-left:11px;padding-right:11px}
    div[data-testid="stTabs"] button[aria-selected="true"]{color:#0e6079}
    @media(max-width:1100px){.pa-kpis{grid-template-columns:repeat(3,1fr)}.pa-people{grid-template-columns:1fr}.pa-stepper{grid-template-columns:repeat(4,1fr)}}
    </style>
    """, unsafe_allow_html=True)


def render(project: dict | None = None, role: str | None = None) -> None:
    _css()
    if is_demo_mode():
        st.error("Production Plan Appraisal is unavailable in demo mode. Connect Supabase and authenticate with a project role.")
        return
    if project is None:
        pid = st.session_state.get("selected_project_id")
        project = pq.project(pid) if pid else None
    if not project:
        st.warning("Select a project first.")
        return

    actor = pq.profile()
    role = role or actor.get("role", "readonly")
    drawings = _safe(lambda: rpq.register(project["id"]), "Plan register") or []
    _hero(project, role)
    _kpis(drawings)
    if role == cfg.ROLE_DESIGNER:
        _designer_new_plan(project)
    if not drawings:
        st.info("No controlled plan has been submitted. The register will appear after the Designer uploads the first PDF revision.")
        return

    left, right = st.columns([3.15, 6.85], gap="medium")
    with left:
        selected = _register(drawings, project["id"])
    drawing = next((x for x in drawings if str(x.get("drawing_id")) == str(selected)), None)
    if drawing:
        with right:
            _dossier(drawing, role, actor, project)


def _hero(project: dict, role: str) -> None:
    role_name = str(role).replace("_", " ").title()
    st.markdown(f'''<div class="pa-shell"><div class="pa-hero">
      <div class="pa-eyebrow">Electronic Plan Appraisal · Controlled Workspace</div>
      <div class="pa-title">Plan Appraisal</div>
      <div class="pa-sub">{_esc(project.get('project_code'))} · {_esc(project.get('name'))} · A single technical register for Designer submissions, revision control, Engineer appraisal, remarks and final approval.</div>
      <div class="pa-secure">● Production Supabase · private document storage · {_esc(role_name)} access</div>
    </div></div>''', unsafe_allow_html=True)


def _kpis(drawings: list[dict]) -> None:
    total = len(drawings); approved = sum(x.get("status") == "approved" for x in drawings)
    remarks = sum(int(x.get("open_remarks") or 0) for x in drawings)
    gm = sum(x.get("status") == "pending_gm_approval" for x in drawings)
    active = sum(x.get("status") not in {"approved", "rejected"} for x in drawings)
    pct = round(approved * 100 / total) if total else 0
    values = [("Plans",total),("In Process",active),("Approved",approved),("Open Remarks",remarks),("Completion",f"{pct}%")]
    cards = ''.join(f'<div class="pa-kpi"><div class="v">{_esc(v)}</div><div class="l">{_esc(k)}</div></div>' for k,v in values)
    st.markdown(f'<div class="pa-kpis">{cards}</div>', unsafe_allow_html=True)


def _register(drawings: list[dict], project_id: str) -> str | None:
    st.markdown('<div class="pa-register-head"><h3>Plan Register</h3><span>Live controlled records</span></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([1.7,1])
    search = c1.text_input("Search plans", placeholder="No., title, discipline", label_visibility="collapsed", key=f"pro_pa_search_{project_id}").strip().lower()
    statuses = sorted({_label(x.get("status")) for x in drawings})
    status = c2.selectbox("Status", ["All",*statuses], label_visibility="collapsed", key=f"pro_pa_status_{project_id}")
    filtered=[]
    for row in drawings:
        hay = ' '.join(str(row.get(k) or '') for k in ("drawing_no","title","discipline","current_file_name")).lower()
        if search and search not in hay: continue
        if status != "All" and _label(row.get("status")) != status: continue
        filtered.append(row)
    if not filtered:
        st.info("No drawings match the current register filters."); return None

    ids=[str(x["drawing_id"]) for x in filtered]
    key=f"pro_pa_selected_{project_id}"
    current=st.session_state.get(key)
    if current not in ids: current=ids[0]; st.session_state[key]=current
    groups=defaultdict(list)
    for row in filtered: groups[str(row.get("discipline") or "Other")].append(row)
    for discipline in sorted(groups):
        st.markdown(f'<div class="pa-disc">{_esc(discipline)} · {len(groups[discipline])}</div>', unsafe_allow_html=True)
        for row in groups[discipline]:
            did=str(row["drawing_id"]); selected=did==current; tone=_tone(str(row.get("status") or ""))
            st.markdown(f'''<div class="pa-row {'sel' if selected else ''}">
              <div class="pa-row-top"><span class="pa-code">{_esc(row.get('drawing_no'))}</span><span class="pa-rev">REV {_esc(row.get('current_revision') or 1)}</span><span class="pa-pill {tone}">{_esc(_label(row.get('status')))}</span></div>
              <div class="pa-row-title">{_esc(row.get('title') or 'Untitled drawing')}</div>
              <div class="pa-row-meta">{_esc(row.get('discipline'))} · {_esc(row.get('engineer_name') or 'Engineer unassigned')}</div>
            </div>''', unsafe_allow_html=True)
            if st.button("Open drawing" if not selected else "Opened", key=f"pro_pa_open_{did}", use_container_width=True, disabled=selected):
                st.session_state[key]=did; st.rerun()
    return st.session_state.get(key)


def _stepper(status: str) -> None:
    order=[x[0] for x in STEPS]
    mapped=status
    aliases={"observation_raised":"under_engineer_review","designer_response":"under_engineer_review","review_resubmitted":"under_engineer_review","revision_pending_dm":"manager_review","surveyor_verification_pending":"under_engineer_review","rejected":"under_engineer_review"}
    mapped=aliases.get(mapped,mapped)
    idx=order.index(mapped) if mapped in order else 0
    bits=[]
    for i,(_,label) in enumerate(STEPS):
        cls="done" if i<idx else ("current" if i==idx else "")
        bits.append(f'<div class="pa-step {cls}"><span>{_esc(label)}</span></div>')
    st.markdown('<div class="pa-stepper">'+''.join(bits)+'</div>', unsafe_allow_html=True)


def _dossier(d: dict, role: str, actor: dict, project: dict) -> None:
    status=str(d.get("status") or ""); tone=_tone(status)
    st.markdown(f'''<div class="pa-dossier">
      <div class="pa-dossier-head"><div class="pa-docline"><span class="pa-docno">{_esc(d.get('drawing_no'))}</span><span class="pa-pill {tone}">{_esc(_label(status))}</span></div>
      <div class="pa-doctitle">{_esc(d.get('title') or 'Untitled drawing')}</div>
      <div class="pa-dossier-meta"><span><b>Discipline</b> {_esc(d.get('discipline'))}</span><span><b>Current revision</b> {_esc(d.get('current_revision') or 1)}</span><span><b>Open remarks</b> {_esc(d.get('open_remarks') or 0)}</span></div></div>
      <div class="pa-people"><div class="pa-person"><span>Designer / Submitter</span><strong>{_esc(d.get('designer_name') or 'Unassigned')}</strong></div><div class="pa-person"><span>Plan Appraisal Manager</span><strong>{_esc(d.get('manager_name') or 'Unassigned')}</strong></div><div class="pa-person"><span>Appraisal Engineer</span><strong>{_esc(d.get('engineer_name') or 'Unassigned')}</strong></div></div>
    </div>''', unsafe_allow_html=True)
    _stepper(status)
    package=_safe(lambda: rpq.revision_package(str(d["drawing_id"])),"Revision package") or []
    remarks=_safe(lambda: rpq.observations(str(d["drawing_id"])),"Remarks") or []
    events=_safe(lambda: rpq.events(str(d["drawing_id"])),"Audit history") or []
    action, files, remarks_tab, audit = st.tabs(["Action Center","Controlled Files","Remarks & Responses","Audit History"])
    with action: _workflow_action(d, role, actor, project)
    with files: _files(d, package)
    with remarks_tab: _remarks(remarks)
    with audit: _events(events)


def _open(path: str, label: str, key: str) -> None:
    try: st.link_button(label, rpq.signed_storage_url(path), key=key, use_container_width=True)
    except Exception as exc: st.warning(f"Controlled file unavailable: {exc}")


def _files(d: dict, package: list[dict]) -> None:
    if not package:
        st.info("No persisted revision package is registered yet."); return
    grouped=defaultdict(list)
    for row in package: grouped[int(row.get("revision_no") or 0)].append(row)
    for rev in sorted(grouped, reverse=True):
        rows=grouped[rev]; base=rows[0]; current=rev==int(d.get("current_revision") or 0)
        with st.container(border=True):
            st.markdown(f'<div class="pa-rev-head"><div class="pa-rev-title">Revision {rev}</div>{"<span class=\"pa-current\">CURRENT CONTROLLED REVISION</span>" if current else ""}</div>', unsafe_allow_html=True)
            st.caption(f"Submitted by {base.get('submitted_by_name') or 'Designer'} · {base.get('submitted_at') or '—'} · {str(base.get('revision_status') or 'submitted').replace('_',' ').title()}")
            c1,c2=st.columns(2)
            with c1:
                st.markdown(f'<div class="pa-filebox"><div class="kind">Designer source document</div><div class="name">{_esc(base.get("designer_file_name") or "No file registered")}</div><div class="meta">Revision {rev} · immutable source record<br>SHA-256: {_esc((base.get("designer_sha256") or "—")[:18])}</div></div>',unsafe_allow_html=True)
                if base.get("designer_storage_path"): _open(base["designer_storage_path"],"Open Designer PDF",f"pro_des_{base['revision_id']}")
            with c2:
                artifacts=[x for x in rows if x.get("artifact_id")]
                if not artifacts: st.info("Engineer appraisal package not yet registered for this revision.")
                for art in artifacts:
                    kind="Marked-up / Appraised Drawing" if art.get("artifact_type")=="MARKED_UP_DRAWING" else "Design Appraisal Report"
                    st.markdown(f'<div class="pa-filebox"><div class="kind">PSB Engineer deliverable</div><div class="name">{_esc(kind)}</div><div class="meta">{_esc(art.get("artifact_file_name"))}<br>{_esc(art.get("artifact_uploaded_by_name") or "Engineer")} · {_esc(art.get("artifact_uploaded_at"))}</div></div>',unsafe_allow_html=True)
                    if art.get("artifact_storage_path"): _open(art["artifact_storage_path"],f"Open {kind}",f"pro_art_{art['artifact_id']}")


def _remarks(rows: list[dict]) -> None:
    if not rows:
        st.success("No technical remarks are recorded against this drawing."); return
    for row in rows:
        resolved=str(row.get("status") or "open").lower() not in {"open","pending"}
        st.markdown(f'''<div class="pa-remark {'resolved' if resolved else ''}"><h4>{_esc(row.get('obs_code') or 'Technical Remark')} · {_esc(row.get('severity') or '—')} · {_esc(str(row.get('status') or 'open').title())}</h4><p>{_esc(row.get('description'))}</p><small>Rule / clause: {_esc(row.get('clause_reference'))} · Drawing ref: {_esc(row.get('drawing_reference'))}</small></div>''',unsafe_allow_html=True)
        if row.get("response"): st.info(f"Designer response: {row['response']}")


def _events(rows: list[dict]) -> None:
    if not rows:
        st.info("No workflow history has been recorded."); return
    for row in rows:
        actor=_safe(lambda uid=row.get("actor_id"): rpq.profile_name(uid),"Actor") or "System"
        st.markdown(f'''<div class="pa-event"><span class="pa-dot"></span><div><b>{_esc(str(row.get('event_type') or 'Event').replace('_',' ').title())} · {_esc(actor)}</b><div>{_esc(row.get('created_at'))} · {_esc(row.get('from_status'))} → {_esc(row.get('to_status'))}</div>{f'<div>{_esc(row.get("note"))}</div>' if row.get('note') else ''}</div></div>''',unsafe_allow_html=True)
