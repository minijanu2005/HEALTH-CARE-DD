"""
Distributed Healthcare Data Management System — Streamlit entry point.
Educational prototype with fictional data only.
"""

from __future__ import annotations

import streamlit as st

from auth import get_session_user
from database import ensure_indexes, get_shared_database, ping_mongodb
from services.migration_service import apply_safe_migrations
from services.user_service import bootstrap_admin_from_env
from ui import (
    admin,
    appointments,
    audit_logs,
    dashboard,
    data_import,
    doctors,
    login,
    medical_records,
    patients,
    reports,
    sync_facilities,
)
from ui.shell import render_sidebar, render_topbar
from ui.styles import HEALTHCARE_CSS

st.set_page_config(
    page_title="CareSync Healthcare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROUTES = {
    "Dashboard": dashboard.render,
    "Patients": patients.render,
    "Medical records": medical_records.render,
    "Doctors": doctors.render,
    "Appointments": appointments.render,
    "Reports": reports.render,
    "Data import": data_import.render,
    "Facilities & sync": sync_facilities.render,
    "Audit logs": audit_logs.render,
    "Administration": admin.render,
}


def _init_app() -> None:
    if st.session_state.get("_app_initialized"):
        return
    ping = ping_mongodb()
    if not ping.get("ok"):
        st.session_state["_db_error"] = ping.get("message", "Database unavailable.")
    else:
        db = get_shared_database()
        ensure_indexes(db)
        apply_safe_migrations(db)
        bootstrap_admin_from_env(db)
    st.session_state["_app_initialized"] = True


def main() -> None:
    st.markdown(HEALTHCARE_CSS, unsafe_allow_html=True)
    _init_app()

    user = get_session_user()
    if user is None:
        st.markdown('<div class="login-page-bg">', unsafe_allow_html=True)
        login.render()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    page = render_sidebar()
    render_topbar(page)
    render_fn = ROUTES.get(page, dashboard.render)
    render_fn()


if __name__ == "__main__":
    main()
