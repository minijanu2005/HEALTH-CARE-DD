"""Application shell: sidebar, top bar, role-aware navigation."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from auth import clear_session_user, get_session_user
from config import get_settings


NAV_ITEMS = [
    ("Dashboard", "📊", {"Administrator", "Doctor", "Receptionist"}),
    ("Patients", "🧑‍⚕️", {"Administrator", "Doctor", "Receptionist"}),
    ("Medical records", "📋", {"Administrator", "Doctor"}),
    ("Doctors", "👨‍⚕️", {"Administrator", "Doctor", "Receptionist"}),
    ("Appointments", "📅", {"Administrator", "Doctor", "Receptionist"}),
    ("Reports", "📈", {"Administrator", "Doctor"}),
    ("Data import", "📥", {"Administrator", "Receptionist"}),
    ("Facilities & sync", "🔄", {"Administrator"}),
    ("Audit logs", "🛡️", {"Administrator"}),
    ("Administration", "⚙️", {"Administrator"}),
]


def render_sidebar() -> str:
    user = get_session_user()
    settings = get_settings()
    if not user:
        return "Dashboard"

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "Dashboard"

    with st.sidebar:
        st.markdown(
            f"""
            <div class="brand-box">
                <div class="brand-title">CareSync HMS</div>
                <div class="brand-sub">{settings.facility_name}</div>
                <div class="brand-sub">Facility · {settings.facility_id}</div>
            </div>
            <div class="sidebar-user">
                <div class="sidebar-user-name">{user['full_name']}</div>
                <div class="sidebar-user-role">{user['role']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_input("Quick search", key="global_search", placeholder="Patient ID or name…", label_visibility="collapsed")
        st.markdown('<div class="nav-label">Main menu</div>', unsafe_allow_html=True)

        allowed = [item for item in NAV_ITEMS if user["role"] in item[2]]
        for name, icon, _ in allowed:
            active = st.session_state.nav_page == name
            btn_type = "primary" if active else "secondary"
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True, type=btn_type):
                st.session_state.nav_page = name
                st.rerun()

        st.markdown("---")
        if st.button("Log out", use_container_width=True):
            clear_session_user()
            st.rerun()

    return st.session_state.nav_page


def render_topbar(page_title: str) -> None:
    user = get_session_user()
    now = datetime.now().strftime("%A, %d %b %Y · %H:%M")
    c1, c2, c3 = st.columns([2.2, 1.2, 0.8])
    with c1:
        st.markdown(
            f'<div class="app-topbar"><div class="crumb">Home / {page_title}</div>'
            f"<h1>{page_title}</h1></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='app-topbar'><div class='crumb'>Today</div><strong>{now}</strong></div>",
            unsafe_allow_html=True,
        )
    with c3:
        if user:
            st.markdown(
                f"<div class='app-topbar user-chip'>"
                f"<div class='crumb'>Signed in</div>"
                f"<strong>{user['username']}</strong></div>",
                unsafe_allow_html=True,
            )
