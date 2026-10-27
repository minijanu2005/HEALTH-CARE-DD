import pandas as pd
import streamlit as st

from auth import require_login
from database import get_shared_database
from models.constants import AppointmentStatus
from permissions import can_manage_appointments
from services.appointment_service import create_appointment, search_appointments, update_appointment_status
from services.doctor_service import list_doctors
from ui.components import begin_panel, end_panel, page_intro
from utils.validators import ValidationError


def render() -> None:
    user = require_login()
    db = get_shared_database()
    actor = {"username": user["username"], "role": user["role"]}

    page_intro("Appointments", "Schedule visits, filter the list, and update status with conflict checks.")

    begin_panel("Appointment list", "Filter by patient, doctor, or status")
    f1, f2, f3 = st.columns(3)
    with f1:
        fp = st.text_input("Patient ID", label_visibility="collapsed", placeholder="Patient ID filter")
    with f2:
        fd = st.text_input("Doctor ID", label_visibility="collapsed", placeholder="Doctor ID filter")
    with f3:
        fs = st.selectbox("Status", ["", *list(AppointmentStatus)], label_visibility="collapsed")

    rows = search_appointments(db, patient_id=fp or None, doctor_id=fd or None, status=fs or None)
    if rows:
        df = pd.DataFrame(
            [
                {
                    "ID": r["appointment_id"],
                    "Patient": r["patient_id"],
                    "Doctor": r["doctor_id"],
                    "DateTime": r["appointment_datetime"],
                    "Status": r["status"],
                }
                for r in rows
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
        df["Date"] = pd.to_datetime(df["DateTime"]).dt.date
        cal = df.groupby("Date").size().reset_index(name="count")
        st.caption("Appointments by date")
        st.bar_chart(cal, x="Date", y="count")
    else:
        st.info("No appointments match your filters.")
    end_panel()

    if can_manage_appointments(user["role"]):
        c1, c2 = st.columns(2)
        with c1:
            begin_panel("Schedule appointment", "")
            doctors = list_doctors(db)
            with st.form("schedule"):
                pid = st.text_input("Patient ID *")
                doc = st.selectbox("Doctor *", [d["doctor_id"] for d in doctors] or [""])
                dt = st.text_input("Date & time (YYYY-MM-DDTHH:MM) *")
                notes = st.text_input("Notes")
                if st.form_submit_button("Schedule", use_container_width=True):
                    try:
                        apt = create_appointment(
                            db,
                            actor=actor,
                            patient_id=pid.strip().upper(),
                            doctor_id=doc,
                            appointment_datetime=dt,
                            notes=notes or None,
                        )
                        st.success(f"Scheduled {apt['appointment_id']}")
                        st.rerun()
                    except (ValidationError, PermissionError) as exc:
                        st.error(str(exc))
            end_panel()
        with c2:
            begin_panel("Update status", "")
            aid = st.text_input("Appointment ID")
            new_status = st.selectbox("New status", list(AppointmentStatus))
            if st.button("Update status", use_container_width=True) and aid:
                try:
                    update_appointment_status(
                        db, actor=actor, appointment_id=aid.strip().upper(), status=new_status
                    )
                    st.success("Updated.")
                    st.rerun()
                except (ValidationError, PermissionError) as exc:
                    st.error(str(exc))
            end_panel()
