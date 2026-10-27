import streamlit as st

from auth import require_login
from database import get_shared_database
from models.constants import Role
from services.report_service import appointment_summary, doctor_workload, patient_summary, patients_to_csv
from ui.components import begin_panel, end_panel, page_intro


def render() -> None:
    user = require_login()
    if user["role"] not in {Role.ADMINISTRATOR, Role.DOCTOR}:
        st.error("Reports are available to administrators and doctors.")
        return

    db = get_shared_database()
    page_intro("Reports & analytics", "Summaries and exports from live MongoDB data.")
    begin_panel("Overview", "")

    ps = patient_summary(db)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total patients", ps["total"])
    c2.metric("Active", ps["active"])
    c3.metric("Inactive", ps["inactive"])

    ap = appointment_summary(db)
    st.markdown("**Appointment summary**")
    st.json(ap)

    st.markdown("**Doctor workload**")
    wl = doctor_workload(db)
    st.dataframe(wl, use_container_width=True)

    csv_data = patients_to_csv(db)
    st.download_button(
        "Export patients CSV",
        data=csv_data,
        file_name="patients_export.csv",
        mime="text/csv",
        use_container_width=True,
    )
    end_panel()
