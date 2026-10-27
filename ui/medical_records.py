import streamlit as st

from auth import require_login
from database import get_shared_database
from permissions import can_create_medical_record, can_view_medical_records
from services.doctor_service import list_doctors
from services.medical_record_service import create_medical_record, get_record, list_records
from ui.components import begin_panel, end_panel, page_intro
from utils.validators import ValidationError


def render() -> None:
    user = require_login()
    if not can_view_medical_records(user["role"]):
        st.error("Your role cannot access medical records.")
        return

    db = get_shared_database()
    actor = {"username": user["username"], "role": user["role"]}

    page_intro("Medical records", "Fictional diagnoses and notes — not real clinical advice.")

    begin_panel("Search records", "Filter by patient, doctor, or keyword")
    f1, f2, f3 = st.columns(3)
    with f1:
        pid = st.text_input("Patient ID filter", label_visibility="collapsed", placeholder="Patient ID")
    with f2:
        did = st.text_input("Doctor ID filter", label_visibility="collapsed", placeholder="Doctor ID")
    with f3:
        q = st.text_input("Search", label_visibility="collapsed", placeholder="Diagnosis / record ID")

    if st.button("Search records", use_container_width=True):
        try:
            records = list_records(db, actor=actor, patient_id=pid or None, doctor_id=did or None, query=q)
            if not records:
                st.info("No records found.")
            for rec in records:
                with st.expander(f"{rec['record_id']} — {rec['diagnosis']} ({rec.get('visit_date')})"):
                    st.write(f"**Patient:** {rec['patient_id']} | **Doctor:** {rec['doctor_id']}")
                    st.write(f"**Prescription:** {rec['prescription']}")
                    st.write(f"**Notes:** {rec['visit_notes']}")
        except (ValidationError, PermissionError) as exc:
            st.error(str(exc))

    rid = st.text_input("Open record by ID")
    if rid and st.button("View record detail"):
        try:
            rec = get_record(db, actor=actor, record_id=rid.strip().upper())
            st.json(rec) if rec else st.warning("Not found.")
        except PermissionError as exc:
            st.error(str(exc))
    end_panel()

    if can_create_medical_record(user["role"]):
        begin_panel("Create medical record", "Associate patient, doctor, and visit date")
        doctors = list_doctors(db)
        doctor_options = {f"{d['full_name']} ({d['doctor_id']})": d["doctor_id"] for d in doctors}
        with st.form("new_record"):
            p = st.text_input("Patient ID *")
            doc_label = st.selectbox("Doctor *", list(doctor_options.keys()) or ["—"])
            visit_date = st.text_input("Visit date (YYYY-MM-DD) *")
            diagnosis = st.text_input("Diagnosis *")
            prescription = st.text_area("Prescription *")
            visit_notes = st.text_area("Visit notes *")
            history = st.text_area("Medical history")
            if st.form_submit_button("Save record", use_container_width=True):
                if not doctor_options:
                    st.error("Add doctors first.")
                else:
                    try:
                        rec = create_medical_record(
                            db,
                            actor=actor,
                            patient_id=p.strip().upper(),
                            doctor_id=doctor_options[doc_label],
                            visit_date=visit_date,
                            diagnosis=diagnosis,
                            prescription=prescription,
                            visit_notes=visit_notes,
                            medical_history=history or None,
                        )
                        st.success(f"Record created: {rec['record_id']}")
                    except (ValidationError, PermissionError) as exc:
                        st.error(str(exc))
        end_panel()
