"""EPAS GM stakeholder registry — reusable external organizations for project creation."""
from __future__ import annotations
import streamlit as st
from config import settings as cfg
from database import production_queries as pq

TYPE_OPTIONS = {
    cfg.ROLE_OWNER: "Owner",
    cfg.ROLE_DESIGNER: "Designer",
    cfg.ROLE_SHIP_MANAGEMENT: "Ship Management",
    cfg.ROLE_SHIPYARD: "Shipyard",
}

TYPE_HELP = {
    cfg.ROLE_OWNER: "Vessel owner / owning company. May initiate In-Service Survey RFIs when assigned to a project.",
    cfg.ROLE_DESIGNER: "Design organization responsible for Plan Appraisal submissions and revisions.",
    cfg.ROLE_SHIP_MANAGEMENT: "Ship management company. May initiate In-Service RFIs and execute corrective actions.",
    cfg.ROLE_SHIPYARD: "Shipyard. May initiate NSC Survey RFIs only.",
}


def _form_defaults():
    return {
        "stakeholder_type": cfg.ROLE_OWNER,
        "company_name": "",
        "registration_no": "",
        "country": "",
        "address": "",
        "city": "",
        "postal_code": "",
        "website": "",
        "contact_name": "",
        "contact_designation": "",
        "contact_email": "",
        "contact_phone": "",
        "contact_mobile": "",
        "notes": "",
    }


def render(role: str):
    if role != cfg.ROLE_GM:
        st.error("Only GM Classification may create stakeholders.")
        return

    st.markdown('<div class="psb-section-eyebrow">STAKEHOLDER DIRECTORY</div>', unsafe_allow_html=True)
    st.markdown("<div class='page-title'>Create New Stakeholder</div>", unsafe_allow_html=True)
    st.caption("Create a reusable Owner, Designer, Ship Management company or Shipyard. It will become selectable in GM Project Creation.")

    c1, c2 = st.columns([3.0, 1.0])
    with c1:
        if st.button("← Back to Projects", key="stakeholder_back_projects", use_container_width=True):
            st.session_state["gm_create_stakeholder_open"] = False
            st.rerun()
    with c2:
        if st.button("Refresh", key="stakeholder_refresh", use_container_width=True):
            try:
                from utils.session_cache import clear_prefixes
                clear_prefixes(["stakeholder_registry"])
            except Exception:
                pass
            st.rerun()

    if "stakeholder_form" not in st.session_state:
        st.session_state["stakeholder_form"] = _form_defaults()
    d = st.session_state["stakeholder_form"]

    left, right = st.columns([1.0, 1.35])
    with left:
        with st.container(border=True):
            st.markdown("#### Stakeholder Type")
            selected = st.radio(
                "Type",
                options=list(TYPE_OPTIONS.keys()),
                format_func=lambda x: TYPE_OPTIONS[x],
                key="stakeholder_form_type",
            )
            d["stakeholder_type"] = selected
            st.info(TYPE_HELP[selected])

    with right:
        with st.form("create_new_stakeholder_v414"):
            st.markdown("#### Company Information")
            c1, c2 = st.columns(2)
            d["company_name"] = c1.text_input("Legal / Company Name *", value=d.get("company_name", ""))
            d["registration_no"] = c2.text_input("Registration / Reference No.", value=d.get("registration_no", ""))
            c1, c2 = st.columns(2)
            d["country"] = c1.text_input("Country", value=d.get("country", ""))
            d["website"] = c2.text_input("Website", value=d.get("website", ""))
            d["address"] = st.text_area("Registered Address", value=d.get("address", ""), height=70)
            c1, c2 = st.columns(2)
            d["city"] = c1.text_input("City", value=d.get("city", ""))
            d["postal_code"] = c2.text_input("Postal Code", value=d.get("postal_code", ""))

            st.markdown("#### Primary Project Contact")
            c1, c2 = st.columns(2)
            d["contact_name"] = c1.text_input("Contact Name *", value=d.get("contact_name", ""))
            d["contact_designation"] = c2.text_input("Designation", value=d.get("contact_designation", ""))
            c1, c2 = st.columns(2)
            d["contact_email"] = c1.text_input("Email", value=d.get("contact_email", ""))
            d["contact_phone"] = c2.text_input("Phone", value=d.get("contact_phone", ""))
            d["contact_mobile"] = st.text_input("Mobile", value=d.get("contact_mobile", ""))
            d["notes"] = st.text_area("GM Notes", value=d.get("notes", ""), height=70)

            submit = st.form_submit_button("Create Stakeholder →", type="primary", use_container_width=True)

        if submit:
            if not d.get("company_name", "").strip():
                st.error("Company name is required.")
                return
            if not d.get("contact_name", "").strip():
                st.error("Primary contact name is required.")
                return
            try:
                result = pq.create_stakeholder_v414(dict(d))
                if result:
                    st.success(f"{TYPE_OPTIONS[selected]} '{result.get('company_name', d['company_name'])}' created and is now available in Create Project.")
                    st.session_state["stakeholder_form"] = _form_defaults()
                    try:
                        from utils.session_cache import clear_prefixes
                        clear_prefixes(["stakeholder_registry", "projects"])
                    except Exception:
                        pass
                    st.rerun()
            except Exception as exc:
                st.error(f"Stakeholder could not be created: {exc}")

    st.markdown("---")
    st.markdown("### Existing Stakeholders")
    st.caption("Only active registry entries are selectable in Project Creation.")
    try:
        rows = pq.stakeholder_registry_v414()
    except Exception as exc:
        st.error(f"Stakeholder directory could not be loaded: {exc}")
        rows = []
    if not rows:
        st.info("No stakeholders have been registered yet.")
        return

    for row in rows:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1.0, 2.6, 2.1])
            c1.markdown(f"**{TYPE_OPTIONS.get(row.get('stakeholder_type'), row.get('stakeholder_type','—'))}**")
            c2.markdown(f"**{row.get('company_name','—')}**")
            c2.caption(f"{row.get('contact_name') or 'No primary contact'} · {row.get('contact_email') or 'No email'}")
            c3.caption(f"{row.get('country') or '—'} · {row.get('registration_no') or 'No registration reference'}")
            c3.caption("Status: Active · Ready for project selection")
