import streamlit as st

from auth import require_login
from database import get_shared_database
from services.bulk_data_service import count_active_patients, generate_fictional_dataset, import_patients_csv
from services.report_service import patients_to_csv
from ui.components import begin_panel, end_panel, page_intro
from utils.validators import ValidationError


def render() -> None:
    user = require_login()
    if user["role"] not in {"Administrator", "Receptionist"}:
        st.error("Only administrators and receptionists can import data.")
        return

    db = get_shared_database()
    actor = {"username": user["username"], "role": user["role"]}

    page_intro("Data import & demo dataset", "Load ~50 fictional records for your viva or import patients from CSV.")

    c1, c2 = st.columns(2)
    with c1:
        begin_panel("One-click demo (recommended)", "Safe for presentations — appends data only")
        current = count_active_patients(db)
        st.metric("Current active patients", current)
        target = st.slider("Target patient count", min_value=20, max_value=100, value=50, step=10)
        if st.button("Generate fictional dataset", type="primary", use_container_width=True):
            with st.spinner("Creating doctors, patients, appointments, and records…"):
                stats = generate_fictional_dataset(db, target_patients=target, actor=actor)
            st.success(
                f"Done! +{stats['patients_added']} patients, +{stats['doctors_added']} doctors, "
                f"+{stats['appointments_added']} appointments, +{stats['records_added']} records."
            )
            st.rerun()
        end_panel()

    with c2:
        begin_panel("Import patients from CSV", "Required: full_name column")
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded is not None:
            text = uploaded.read().decode("utf-8-sig")
            if st.button("Import CSV now", use_container_width=True):
                try:
                    result = import_patients_csv(db, actor=actor, csv_text=text)
                    st.success(f"Imported {result['imported']} rows ({result['skipped']} skipped).")
                    st.rerun()
                except ValidationError as exc:
                    st.error(str(exc))

        sample = (
            "full_name,date_of_birth,gender,phone,email,address\n"
            "Sample Person,1995-06-01,Female,+1 555 9999,sample@example.test,Demo City"
        )
        st.download_button(
            "Download sample CSV template",
            data=sample,
            file_name="patient_import_template.csv",
            mime="text/csv",
            use_container_width=True,
        )
        end_panel()

    begin_panel("Export current patients", "Download CSV snapshot")
    st.download_button(
        "Export patients CSV",
        data=patients_to_csv(db),
        file_name="patients_export.csv",
        mime="text/csv",
        use_container_width=True,
    )
    end_panel()
