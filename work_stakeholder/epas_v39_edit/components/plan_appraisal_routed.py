"""PSB Plan Appraisal v4.3 · exact role-routed production workspace."""
from __future__ import annotations

import html
from collections import defaultdict

import streamlit as st

from config import settings as cfg
from config.supabase_client import is_demo_mode
from database import production_queries as pq
from database import real_plan_queries as rpq
from database import plan_appraisal_workflow_v43 as wf

LABELS={
 "submitted":"Received by GM","assigned_manager":"With Plan Appraisal Manager",
 "assigned_engineer":"With Plan Appraisal Engineer","under_engineer_review":"Engineer Appraisal",
 "observation_raised":"Engineer Remarks","designer_response":"With Designer",
 "revision_pending_dm":"Revision with Manager","review_resubmitted":"Engineer Re-appraisal",
 "manager_review":"Manager Review","pending_gm_approval":"With GM for Approval",
 "approved":"Approved / Delivered","rejected":"Return Decision"
}
STEPS=["Designer","GM Intake","Manager","Engineer","Manager Review","GM Approval","Designer Delivery"]


def esc(x): return html.escape(str(x if x not in (None,"") else "—"))
def label(x): return LABELS.get(str(x or ""),str(x or "—").replace("_"," ").title())

def safe(fn,title):
    try:return fn()
    except Exception as e: st.error(f"{title}: {e}");return None


def css():
 st.markdown("""<style>
 .rpa-hero{background:linear-gradient(135deg,#04262E,#07445A);color:white;padding:22px 24px;border-radius:17px;margin-bottom:12px;box-shadow:0 12px 28px rgba(4,38,46,.15)}
 .rpa-hero .e{font-size:10px;letter-spacing:.14em;font-weight:800;color:#7fe1d1}.rpa-hero h1{font-size:27px;margin:3px 0}.rpa-hero p{font-size:12px;color:#c6dadd;margin:0}
 .rpa-flow{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin:12px 0 18px}.rpa-flow div{background:#fff;border:1px solid #dce6e9;border-radius:10px;padding:9px 5px;text-align:center;font-size:9px;font-weight:750;color:#56717a}.rpa-flow div:before{content:'→';float:right;color:#9eb0b6}.rpa-flow div:last-child:before{content:''}
 .rpa-kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:14px}.rpa-k{background:white;border:1px solid #e0e8eb;border-radius:11px;padding:11px 13px}.rpa-k b{font-size:20px;color:#103c48}.rpa-k span{display:block;font-size:9px;color:#758b92;text-transform:uppercase;font-weight:800;letter-spacing:.07em}
 .rpa-group{font-size:9px;font-weight:850;color:#607981;text-transform:uppercase;letter-spacing:.09em;margin:10px 0 5px}.rpa-card{border:1px solid #dfe7ea;border-radius:10px;padding:10px;margin-bottom:6px;background:#fff}.rpa-card.sel{border-color:#00A884;background:#f3fcf9}.rpa-card .top{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.rpa-no{font-size:11px;font-weight:850;color:#0d5362}.rpa-rev{font-size:9px;background:#edf3f4;padding:2px 5px;border-radius:5px;color:#536c73}.rpa-status{font-size:8px;font-weight:850;padding:3px 7px;border-radius:999px;background:#e7f5f2;color:#08745e}.rpa-name{font-size:11px;color:#2b434b;margin-top:4px}
 .rpa-head{border:1px solid #dce5e8;border-radius:14px;background:white;overflow:hidden}.rpa-title{padding:16px 18px;border-bottom:1px solid #e7edef}.rpa-title .no{font-size:11px;font-weight:850;color:#0c6973}.rpa-title h2{font-size:20px;color:#153c48;margin:3px 0}.rpa-title p{font-size:10px;color:#71868c;margin:0}.rpa-people{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;padding:11px 18px}.rpa-person{background:#f8fafb;border:1px solid #e4eaec;border-radius:9px;padding:8px}.rpa-person span{display:block;font-size:8px;text-transform:uppercase;color:#829399;font-weight:800}.rpa-person b{font-size:11px;color:#29444c}
 .rpa-route{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin:10px 0}.rpa-route div{height:5px;background:#dce5e8;border-radius:9px}.rpa-route .done{background:#00A884}.rpa-route .now{background:#d6a139}
 .rpa-file{border:1px solid #e1e8ea;border-radius:10px;padding:10px;background:#fbfcfc;margin-bottom:7px}.rpa-file small{display:block;color:#7c8f95;font-size:9px}.rpa-file b{font-size:11px;color:#29454d}.rpa-delivered{background:#eaf8f3;border:1px solid #bfe6d7;border-radius:11px;padding:12px;color:#176b53;font-size:11px;font-weight:700}
 @media(max-width:1000px){.rpa-flow,.rpa-route{grid-template-columns:repeat(4,1fr)}.rpa-kpis{grid-template-columns:repeat(3,1fr)}.rpa-people{grid-template-columns:1fr}}
 </style>""",unsafe_allow_html=True)


def render(project=None,role=None):
 css()
 if is_demo_mode(): st.error("This Plan Appraisal workspace requires production Supabase.");return
 if project is None:
  pid=st.session_state.get("selected_project_id");project=pq.project(pid) if pid else None
 if not project: st.warning("Select a project first.");return
 me=pq.profile();role=role or me.get("role")
 drawings=safe(lambda:rpq.register(project["id"]),"Plan register") or []
 st.markdown(f'<div class="rpa-hero"><div class="e">PAKISTAN SHIPPING BUREAU · ELECTRONIC PLAN APPRAISAL</div><h1>Plan Appraisal</h1><p>{esc(project.get("project_code"))} · {esc(project.get("name"))} · Controlled role-routed drawing approval</p></div>',unsafe_allow_html=True)
 st.markdown('<div class="rpa-flow">'+''.join(f'<div>{x}</div>' for x in STEPS)+'</div>',unsafe_allow_html=True)
 k=[("Plans",len(drawings)),("GM Intake",sum(x.get("status")=="submitted" for x in drawings)),("Engineer",sum(x.get("status") in {"assigned_engineer","under_engineer_review","review_resubmitted"} for x in drawings)),("Manager Review",sum(x.get("status")=="manager_review" for x in drawings)),("Approved",sum(x.get("status")=="approved" for x in drawings))]
 st.markdown('<div class="rpa-kpis">'+''.join(f'<div class="rpa-k"><b>{v}</b><span>{esc(n)}</span></div>' for n,v in k)+'</div>',unsafe_allow_html=True)
 if role==cfg.ROLE_DESIGNER: new_plan(project)
 if not drawings: st.info("No Designer drawing has been submitted for this project.");return
 left,right=st.columns([3.1,6.9],gap="medium")
 with left: did=register(drawings,project["id"])
 d=next((x for x in drawings if str(x["drawing_id"])==str(did)),None)
 if d:
  with right: dossier(d,role,me,project)


def new_plan(project):
 with st.expander("+ Submit New Drawing",expanded=False):
  st.caption("Designer only · this PDF becomes controlled Revision 1 and is received by GM.")
  c1,c2=st.columns(2);no=c1.text_input("Drawing number *",key=f"rpa_no_{project['id']}");title=c2.text_input("Drawing title *",key=f"rpa_title_{project['id']}")
  disc=st.selectbox("Discipline",cfg.DISCIPLINES,key=f"rpa_disc_{project['id']}");pdf=st.file_uploader("Drawing PDF *",type=["pdf"],key=f"rpa_pdf_{project['id']}");note=st.text_area("Submission note *",key=f"rpa_note_{project['id']}")
  if st.button("Submit to GM",type="primary",key=f"rpa_submit_{project['id']}"):
   if safe(lambda:wf.submit_initial(project["id"],no,title,disc,pdf,note),"Submission"): st.success("Drawing received by GM.");st.rerun()


def register(rows,pid):
 c1,c2=st.columns([1.6,1]);q=c1.text_input("Search",placeholder="Drawing no. or title",label_visibility="collapsed",key=f"rpa_search_{pid}").lower();statuses=sorted({label(x.get("status")) for x in rows});sf=c2.selectbox("Status",["All",*statuses],label_visibility="collapsed",key=f"rpa_sf_{pid}")
 filtered=[x for x in rows if (not q or q in (' '.join(str(x.get(k) or '') for k in ('drawing_no','title','discipline'))).lower()) and (sf=="All" or label(x.get('status'))==sf)]
 if not filtered: st.info("No plans match filters.");return None
 ids=[str(x['drawing_id']) for x in filtered];key=f"rpa_sel_{pid}";cur=st.session_state.get(key)
 if cur not in ids:cur=ids[0];st.session_state[key]=cur
 groups=defaultdict(list)
 for x in filtered:groups[str(x.get('discipline') or 'Other')].append(x)
 for g in sorted(groups):
  st.markdown(f'<div class="rpa-group">{esc(g)} · {len(groups[g])}</div>',unsafe_allow_html=True)
  for x in groups[g]:
   did=str(x['drawing_id']);sel=did==cur
   st.markdown(f'<div class="rpa-card {"sel" if sel else ""}"><div class="top"><span class="rpa-no">{esc(x.get("drawing_no"))}</span><span class="rpa-rev">REV {esc(x.get("current_revision") or 1)}</span><span class="rpa-status">{esc(label(x.get("status")))}</span></div><div class="rpa-name">{esc(x.get("title"))}</div></div>',unsafe_allow_html=True)
   if st.button("Open" if not sel else "Selected",key=f"rpa_open_{did}",use_container_width=True,disabled=sel):st.session_state[key]=did;st.rerun()
 return st.session_state[key]


def route_index(status):
 m={"submitted":1,"assigned_manager":2,"revision_pending_dm":2,"assigned_engineer":3,"under_engineer_review":3,"review_resubmitted":3,"manager_review":4,"pending_gm_approval":5,"approved":6,"designer_response":6,"rejected":5}
 return m.get(status,0)


def dossier(d,role,me,project):
 status=str(d.get('status') or '');idx=route_index(status)
 st.markdown(f'<div class="rpa-head"><div class="rpa-title"><span class="no">{esc(d.get("drawing_no"))} · REV {esc(d.get("current_revision") or 1)}</span><h2>{esc(d.get("title"))}</h2><p>{esc(d.get("discipline"))} · {esc(label(status))}</p></div><div class="rpa-people"><div class="rpa-person"><span>Designer</span><b>{esc(d.get("designer_name") or "Unassigned")}</b></div><div class="rpa-person"><span>Plan Appraisal Manager</span><b>{esc(d.get("manager_name") or "Unassigned")}</b></div><div class="rpa-person"><span>Plan Appraisal Engineer</span><b>{esc(d.get("engineer_name") or "Unassigned")}</b></div></div></div>',unsafe_allow_html=True)
 st.markdown('<div class="rpa-route">'+''.join(f'<div class="{"done" if i<idx else "now" if i==idx else ""}"></div>' for i in range(7))+'</div>',unsafe_allow_html=True)
 action,files,remarks,audit=st.tabs(["My Action","Revision & Files","Remarks","Audit Trail"])
 with action: action_center(d,role,me,project)
 with files: files_view(d)
 with remarks: remarks_view(d)
 with audit: audit_view(d)


def action_center(d,role,me,project):
 status=str(d.get('status') or '');did=str(d['drawing_id'])
 if role==cfg.ROLE_DESIGNER and str(d.get('designer_id') or '')==str(me.get('id')):
  if status in {'designer_response','rejected'}:
   st.markdown("#### Submit requested revision")
   st.caption(f"Current revision {d.get('current_revision') or 1} is retained. The new PDF creates the next immutable revision and returns through GM/Manager routing.")
   pdf=st.file_uploader("Revised Drawing PDF *",type=['pdf'],key=f"rpa_rev_pdf_{did}");note=st.text_area("Revision / response note *",key=f"rpa_rev_note_{did}")
   if st.button("Submit New Revision",type='primary',key=f"rpa_rev_submit_{did}"):
    if safe(lambda:wf.submit_revision(did,pdf,note),"Revision submission"):st.success("New revision submitted.");st.rerun()
  elif status=='approved': st.markdown('<div class="rpa-delivered">✓ Final GM approval completed. The approved PSB appraisal package is available to the Designer in Revision & Files.</div>',unsafe_allow_html=True)
  else: st.info(f"Your drawing is currently: {label(status)}. No Designer action is required.")
  return
 if role==cfg.ROLE_GM and status=='submitted':
  st.markdown("#### GM Intake · Route to Plan Appraisal Manager");st.caption("GM does not upload or technically appraise the drawing. Select the responsible Manager and route it.")
  managers=wf.managers_for_project(project['id'])
  if not managers:st.warning("No Plan Appraisal Manager is assigned to this project.");return
  by={str(x['id']):x for x in managers};mid=st.selectbox("Plan Appraisal Manager *",list(by),format_func=lambda x:by[x].get('full_name') or x,key=f"rpa_mgr_{did}")
  if st.button("Route to Manager",type='primary',key=f"rpa_mgr_send_{did}"):
   if safe(lambda:wf.gm_route_to_manager(did,mid),"GM routing"):st.success("Routed to Plan Appraisal Manager.");st.rerun()
  return
 if role==cfg.ROLE_DM and str(d.get('manager_id') or '')==str(me.get('id')) and status in {'assigned_manager','revision_pending_dm'}:
  st.markdown("#### Manager Allocation · Route to Engineer");st.caption("Manager routes only. Select an eligible authorised Plan Appraisal Engineer.")
  eng=safe(lambda:wf.eligible_engineers(project['id'],str(d.get('discipline') or '')),"Eligibility") or []
  if not eng:st.warning("No eligible Engineer is currently available for this discipline.");return
  by={str(x.get('user_id') or x.get('id')):x for x in eng};eid=st.selectbox("Plan Appraisal Engineer *",list(by),format_func=lambda x:by[x].get('full_name') or x,key=f"rpa_eng_{did}")
  if st.button("Route to Engineer",type='primary',key=f"rpa_eng_send_{did}"):
   if safe(lambda:wf.manager_route_to_engineer(did,eid),"Engineer routing"):st.success("Routed to Plan Appraisal Engineer.");st.rerun()
  return
 if role==cfg.ROLE_ENGINEER and str(d.get('engineer_id') or '')==str(me.get('id')) and status in {'assigned_engineer','under_engineer_review','review_resubmitted'}:
  st.markdown("#### Engineer Appraisal")
  st.caption("Review the Designer PDF, select the appraisal result, enter appraisal note/remarks and attach PSB appraisal file(s).")
  result=st.selectbox("Appraisal Result *",['APPROVED','APPROVED_AS_AMENDED','INFORMATION','REJECTED'],format_func=lambda x:x.replace('_',' ').title(),key=f"rpa_result_{did}")
  note=st.text_area("Appraisal Note *",key=f"rpa_app_note_{did}");remark=st.text_area("Technical Remark / Amendment",key=f"rpa_remark_{did}")
  c1,c2=st.columns(2);marked=c1.file_uploader("Appraised / Marked Drawing PDF",type=['pdf'],key=f"rpa_marked_{did}");report=c2.file_uploader("Design Appraisal File PDF",type=['pdf'],key=f"rpa_report_{did}")
  if st.button("Submit Appraisal to Manager",type='primary',key=f"rpa_app_submit_{did}"):
   if safe(lambda:wf.engineer_submit_appraisal(did,result,note,remark,marked,report),"Appraisal submission"):st.success("Appraisal sent to Plan Appraisal Manager.");st.rerun()
  return
 if role==cfg.ROLE_DM and str(d.get('manager_id') or '')==str(me.get('id')) and status=='manager_review':
  st.markdown("#### Manager Review · Route to GM");st.caption("Review the Engineer package. Do not upload technical files.")
  action=st.radio("Manager action",['FORWARD_TO_GM','RETURN_TO_ENGINEER','SEND_TO_GM_FOR_DESIGNER_RETURN'],format_func=lambda x:{'FORWARD_TO_GM':'Forward to GM for approval','RETURN_TO_ENGINEER':'Return to Engineer','SEND_TO_GM_FOR_DESIGNER_RETURN':'Send to GM recommending return to Designer'}[x],key=f"rpa_dm_action_{did}")
  note=st.text_area("Manager routing / review note",key=f"rpa_dm_note_{did}")
  if st.button("Complete Manager Review",type='primary',key=f"rpa_dm_submit_{did}"):
   if safe(lambda:wf.manager_review(did,action,note),"Manager review"):st.success("Manager review completed.");st.rerun()
  return
 if role==cfg.ROLE_GM and status=='pending_gm_approval':
  st.markdown("#### GM Final Decision");st.caption("Review the complete Designer + PSB appraisal package. GM does not upload technical files.")
  action=st.radio("GM decision",['APPROVE_AND_DELIVER','RETURN_TO_DESIGNER'],format_func=lambda x:'Approve and deliver to Designer' if x=='APPROVE_AND_DELIVER' else 'Return to Designer for revision',key=f"rpa_gm_action_{did}");note=st.text_area("GM decision note",key=f"rpa_gm_note_{did}")
  if st.button("Record Final Decision",type='primary',key=f"rpa_gm_submit_{did}"):
   if safe(lambda:wf.gm_final_decision(did,action,note),"GM decision"):st.success("GM decision recorded and routed to Designer.");st.rerun()
  return
 if status=='approved':st.success("Approved by GM. Final controlled package is delivered in-system to the Designer and remains visible to authorised project members.")
 else:st.info(f"Current stage: {label(status)}. There is no action for your role at this stage.")


def files_view(d):
 package=safe(lambda:wf.package(str(d['drawing_id'])),"Revision package") or []
 if not package:st.info("No revision files registered.");return
 groups=defaultdict(list)
 for x in package:groups[int(x.get('revision_no') or 0)].append(x)
 for rev in sorted(groups,reverse=True):
  rows=groups[rev];base=rows[0]
  with st.container(border=True):
   st.markdown(f"#### Revision {rev}" + (" · CURRENT" if rev==int(d.get('current_revision') or 0) else ""))
   c1,c2=st.columns(2)
   with c1:
    st.markdown(f'<div class="rpa-file"><small>DESIGNER DRAWING</small><b>{esc(base.get("designer_file_name"))}</b><small>{esc(base.get("submitted_by_name") or "Designer")} · {esc(base.get("submitted_at"))}</small></div>',unsafe_allow_html=True)
    if base.get('designer_storage_path'):st.link_button("Open Designer Drawing",wf.signed_url(base['designer_storage_path']),use_container_width=True,key=f"rpa_des_file_{base['revision_id']}")
   with c2:
    arts=[x for x in rows if x.get('artifact_id')]
    if not arts:st.info("PSB appraisal file not yet uploaded for this revision.")
    for a in arts:
     kind='Appraised / Marked Drawing' if a.get('artifact_type')=='MARKED_UP_DRAWING' else 'Design Appraisal File'
     st.markdown(f'<div class="rpa-file"><small>PSB APPRAISAL</small><b>{esc(kind)}</b><small>{esc(a.get("artifact_file_name"))} · {esc(a.get("artifact_uploaded_by_name") or "Engineer")}</small></div>',unsafe_allow_html=True)
     if a.get('artifact_storage_path'):st.link_button(f"Open {kind}",wf.signed_url(a['artifact_storage_path']),use_container_width=True,key=f"rpa_art_{a['artifact_id']}")
 if d.get('status')=='approved':st.markdown('<div class="rpa-delivered">✓ FINAL PACKAGE DELIVERED TO DESIGNER · GM APPROVED</div>',unsafe_allow_html=True)


def remarks_view(d):
 rows=safe(lambda:wf.remarks(str(d['drawing_id'])),"Remarks") or []
 if not rows:st.success("No technical remarks recorded.");return
 for x in rows:
  with st.container(border=True):
   st.markdown(f"**{esc(x.get('obs_code') or 'Remark')} · {esc(str(x.get('status') or 'open').title())}**");st.write(x.get('description') or '—')
   if x.get('response'):st.info(f"Designer response: {x['response']}")


def audit_view(d):
 rows=safe(lambda:wf.events(str(d['drawing_id'])),"Audit trail") or []
 if not rows:st.info("No workflow events recorded.");return
 for x in rows:
  who=safe(lambda uid=x.get('actor_id'):rpq.profile_name(uid),"Actor") or 'System'
  st.markdown(f"**{esc(str(x.get('event_type') or 'Event').replace('_',' ').title())}** · {esc(who)}");st.caption(f"{esc(x.get('created_at'))} · {esc(x.get('from_status'))} → {esc(x.get('to_status'))}")
  if x.get('note'):st.write(x['note'])
