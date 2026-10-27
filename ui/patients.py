import streamlit as st

from auth import require_login
from database import get_shared_database
from permissions import can_delete_patient, can_edit_patient
from services.patient_service import (
    create_patient,
    deactivate_patient,
    delete_patient,
    get_patient,
    list_patients,
    update_patient,
)
from ui.components import begin_panel, end_panel, page_intro
from utils.validators import ValidationError


def render() -> None:
    user = require_login()
    db = get_shared_database()
    actor = {"username": user["username"], "role": user["role"]}

    page_intro("Patient management", "Register fictional patients, search, update, and manage access by role.")

    tab_list, tab_register, tab_profile = st.tabs(["Directory", "Register", "Profile & edit"])

    with tab_list:
        begin_panel("Patient directory", "Search by ID or name")
        default_q = st.session_state.get("global_search", "")
        q = st.text_input("Search by ID or name", value=default_q)
        page = st.number_input("Page", min_value=1, value=1, step=1)
        page_size = st.selectbox("Page size", [10, 25, 50], index=1)
        rows = list_patients(db, query=q, skip=(page - 1) * page_size, limit=page_size)
        if not rows:
            st.info("No patients found.")
        else:
            st.dataframe(
                [
                    {
                        "ID": r["patient_id"],
                        "Name": r["full_name"],
                        "DOB": r["date_of_birth"],
                        "Facility": r.get("facility_id"),
                        "Active": r.get("active", True),
                    }
                    for r in rows
                ],
                use_container_width=True,
                hide_index=True,
            )
        end_panel()

    with tab_register:
        if not can_edit_patient(user["role"]):
            st.error("Your role cannot register patients.")
        else:
            with st.form("register_patient"):
                name = st.text_input("Full name *")
                dob = st.text_input("Date of birth (YYYY-MM-DD) *")
                gender = st.selectbox("Gender *", ["Female", "Male", "Non-binary", "Prefer not to say"])
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                address = st.text_area("Address")
                if st.form_submit_button("Register patient"):
                    try:
                        doc = create_patient(
                            db,
                            actor=actor,
                            full_name=name,
                            date_of_birth=dob,
                            gender=gender,
                            phone=phone or None,
                            email=email or None,
                            address=address or None,
                        )
                        st.success(f"Registered {doc['patient_id']}")
                    except (ValidationError, PermissionError) as exc:
                        st.error(str(exc))

    with tab_profile:
        pid = st.text_input("Patient ID")
        if pid and st.button("Load profile"):
            p = get_patient(db, pid.strip().upper())
            if p:
                st.json(p)
            else:
                st.error("Not found.")
        if can_edit_patient(user["role"]):
            with st.form("update_patient"):
                pid2 = st.text_input("Patient ID to update *")
                name = st.text_input("New name")
                dob = st.text_input("New DOB")
                if st.form_submit_button("Save changes"):
                    try:
                        update_patient(
                            db,
                            actor=actor,
                            patient_id=pid2.strip().upper(),
                            full_name=name or None,
                            date_of_birth=dob or None,
                        )
                        st.success("Updated.")
                    except (ValidationError, PermissionError) as exc:
                        st.error(str(exc))
            confirm = st.checkbox("Confirm deactivation")
            if st.button("Deactivate patient") and confirm:
                try:
                    deactivate_patient(db, actor=actor, patient_id=pid.strip().upper())
                    st.success("Patient deactivated.")
                except (ValidationError, PermissionError) as exc:
                    st.error(str(exc))
        if can_delete_patient(user["role"]):
            confirm_del = st.checkbox("Confirm permanent delete (admin)")
            if st.button("Delete patient") and confirm_del:
                try:
                    delete_patient(db, actor=actor, patient_id=pid.strip().upper())
                    st.success("Deleted.")
                except (ValidationError, PermissionError) as exc:
                    st.error(str(exc))
