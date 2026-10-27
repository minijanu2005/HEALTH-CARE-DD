import streamlit as st

from auth import require_login
from database import get_shared_database
from permissions import can_manage_doctors
from services.doctor_service import (
    create_doctor,
    doctor_appointment_count,
    list_doctors,
    set_doctor_active,
    update_doctor,
)
from ui.components import begin_panel, end_panel, page_intro
from utils.validators import ValidationError


def render() -> None:
    user = require_login()
    db = get_shared_database()
    actor = {"username": user["username"], "role": user["role"]}

    page_intro("Doctor directory", "Search specialists, view workload, and manage active status.")

    begin_panel("Search & filters", "Find doctors by name, ID, or specialty")
    c1, c2 = st.columns(2)
    with c1:
        q = st.text_input("Search doctors", label_visibility="collapsed", placeholder="Search doctors")
    with c2:
        specialty = st.text_input("Specialty filter", label_visibility="collapsed", placeholder="Filter by specialty")
    rows = list_doctors(db, active_only=False, specialty=specialty or None, query=q)
    st.dataframe(
        [
            {
                "ID": d["doctor_id"],
                "Name": d["full_name"],
                "Specialty": d["specialty"],
                "Appointments": doctor_appointment_count(db, d["doctor_id"]),
                "Active": d.get("active", True),
            }
            for d in rows
        ],
        use_container_width=True,
        hide_index=True,
    )
    end_panel()

    if can_manage_doctors(user["role"]):
        t1, t2 = st.tabs(["Add doctor", "Edit / status"])
        with t1:
            begin_panel("Add new doctor", "Administrators only")
            with st.form("add_doctor"):
                name = st.text_input("Full name *")
                spec = st.text_input("Specialty *")
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                if st.form_submit_button("Add doctor", use_container_width=True):
                    try:
                        doc = create_doctor(
                            db,
                            actor=actor,
                            full_name=name,
                            specialty=spec,
                            phone=phone or None,
                            email=email or None,
                        )
                        st.success(f"Added {doc['doctor_id']}")
                        st.rerun()
                    except (ValidationError, PermissionError) as exc:
                        st.error(str(exc))
            end_panel()
        with t2:
            begin_panel("Update doctor profile", "")
            did = st.text_input("Doctor ID")
            name = st.text_input("New name")
            spec = st.text_input("New specialty")
            if st.button("Save doctor profile", use_container_width=True) and did:
                try:
                    update_doctor(
                        db,
                        actor=actor,
                        doctor_id=did.strip().upper(),
                        full_name=name or None,
                        specialty=spec or None,
                    )
                    st.success("Updated.")
                except (ValidationError, PermissionError) as exc:
                    st.error(str(exc))
            active = st.radio("Status", ["Active", "Inactive"], horizontal=True)
            if st.button("Update status", use_container_width=True) and did:
                try:
                    set_doctor_active(db, actor=actor, doctor_id=did.strip().upper(), active=active == "Active")
                    st.success("Status updated.")
                    st.rerun()
                except (ValidationError, PermissionError) as exc:
                    st.error(str(exc))
            end_panel()
