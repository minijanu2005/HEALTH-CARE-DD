import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from auth import get_session_user, require_login
from config import get_settings
from database import get_shared_database
from services.bulk_data_service import count_active_patients, generate_fictional_dataset
from services.dashboard_service import (
    appointments_by_status,
    appointments_monthly,
    doctor_appointment_share,
    get_dashboard_stats,
    patient_registration_trend,
    queue_status_distribution,
    recent_audit_logs,
    recent_medical_records,
    recent_patients,
    todays_appointments,
    upcoming_appointments,
)
from ui.components import kpi_card, panel


def _greeting() -> str:
    hour = pd.Timestamp.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def render() -> None:
    user = require_login()
    db = get_shared_database()
    settings = get_settings()
    stats = get_dashboard_stats(db)

    st.markdown(
        f"""
        <div class="hero-banner">
            <h2>{_greeting()}, {user['full_name']}!</h2>
            <p>Here's what's happening at <strong>{settings.facility_name}</strong> today — all metrics from live MongoDB data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if count_active_patients(db) < 10:
        st.warning("Dashboard looks empty. Load fictional demo data for your presentation.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Load 50 fictional records", type="primary", use_container_width=True):
                with st.spinner("Generating demo dataset…"):
                    result = generate_fictional_dataset(db, target_patients=50, actor={"username": user["username"], "role": user["role"]})
                st.success(
                    f"Added {result['patients_added']} patients, {result['appointments_added']} appointments, "
                    f"{result['records_added']} records."
                )
                st.rerun()
        with c2:
            st.caption("Or use **Data import** from the sidebar (CSV upload).")

    r1 = st.columns(5)
    kpis = [
        ("Total patients", stats["patients"], "Active registrations", "#2563EB"),
        ("Active doctors", stats["doctors"], "On duty directory", "#0EA5E9"),
        ("Today's appointments", stats["today"], "Scheduled for today", "#7C3AED"),
        ("Pending", stats["pending"], "Awaiting visit", "#F59E0B"),
        ("Medical records", stats["records"], "Fictional clinical notes", "#059669"),
    ]
    for col, (label, val, sub, accent) in zip(r1, kpis):
        with col:
            kpi_card(label, val, sub, accent)

    qa = st.columns(4)
    if qa[0].button("＋ Register patient", use_container_width=True):
        st.session_state.nav_page = "Patients"
        st.rerun()
    if qa[1].button("📅 Schedule appointment", use_container_width=True):
        st.session_state.nav_page = "Appointments"
        st.rerun()
    if qa[2].button("📋 Add medical record", use_container_width=True):
        st.session_state.nav_page = "Medical records"
        st.rerun()
    if qa[3].button("📈 Open reports", use_container_width=True):
        st.session_state.nav_page = "Reports"
        st.rerun()

    left, mid, right = st.columns([1.2, 1.2, 0.9])

    with left:
        panel("Appointment statistics", "Monthly volume by status")
        monthly = appointments_monthly(db)
        if monthly:
            mdf = pd.DataFrame(monthly)
            fig = px.bar(
                mdf,
                x="month",
                y="count",
                color="status",
                barmode="stack",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(margin=dict(l=8, r=8, t=8, b=8), legend_title_text="Status")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No appointments yet.")

    with mid:
        panel("Patient registration trend", "New patients over time")
        trend = patient_registration_trend(db)
        if trend:
            tdf = pd.DataFrame(trend)
            fig2 = px.area(tdf, x="date", y="registrations", template="plotly_white", color_discrete_sequence=["#2563EB"])
            fig2.update_layout(margin=dict(l=8, r=8, t=8, b=8))
            st.plotly_chart(fig2, use_container_width=True)

        panel("Queue / visit status", "Distribution (pie)")
        qdist = queue_status_distribution(db)
        if sum(qdist.values()) > 0:
            pie_df = pd.DataFrame({"status": list(qdist.keys()), "count": list(qdist.values())})
            fig_pie = px.pie(
                pie_df,
                names="status",
                values="count",
                hole=0.55,
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_pie.update_layout(margin=dict(l=8, r=8, t=8, b=8))
            st.plotly_chart(fig_pie, use_container_width=True)

    with right:
        panel("Top doctors by appointments", "Workload snapshot")
        tops = doctor_appointment_share(db, limit=5)
        if tops:
            tdf = pd.DataFrame(tops)
            fig_d = px.bar(
                tdf,
                x="appointments",
                y="doctor",
                orientation="h",
                template="plotly_white",
                color="appointments",
                color_continuous_scale="Blues",
            )
            fig_d.update_layout(showlegend=False, margin=dict(l=8, r=8, t=8, b=8), coloraxis_showscale=False)
            st.plotly_chart(fig_d, use_container_width=True)

        by_status = appointments_by_status(db)
        if by_status:
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=list(by_status.keys()),
                        values=list(by_status.values()),
                        hole=0.62,
                        marker=dict(colors=["#3B82F6", "#10B981", "#EF4444", "#F59E0B"]),
                    )
                ]
            )
            fig_donut.update_layout(margin=dict(l=8, r=8, t=8, b=8), showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    panel("Today's appointments", "Live schedule")
    today_rows = todays_appointments(db)
    if today_rows:
        st.dataframe(
            [
                {
                    "Time": r["appointment_datetime"],
                    "Patient": r["patient_id"],
                    "Doctor": r["doctor_id"],
                    "Status": r["status"],
                }
                for r in today_rows
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No appointments today — demo data includes nearby dates.")
    st.markdown("</div>", unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        panel("Recent patients", "")
        for p in recent_patients(db):
            st.markdown(f"**{p['full_name']}**  \n`{p['patient_id']}`")
        st.markdown("</div>", unsafe_allow_html=True)
    with b2:
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        panel("Upcoming consultations", "")
        for a in upcoming_appointments(db):
            st.markdown(f"**{a['appointment_datetime']}** — {a['patient_id']} / {a['doctor_id']}")
        st.markdown("</div>", unsafe_allow_html=True)
    with b3:
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        panel("Recent medical records", "")
        for rec in recent_medical_records(db):
            st.markdown(f"**{rec['diagnosis']}**  \n{rec['record_id']} · {rec['patient_id']}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    panel("Recent activity", "Audit trail excerpt")
    logs = recent_audit_logs(db)
    if logs:
        st.dataframe(
            [
                {
                    "Time": log.get("timestamp"),
                    "User": log.get("actor_username"),
                    "Action": log.get("action"),
                    "Entity": f"{log.get('entity_type')}:{log.get('entity_id')}",
                }
                for log in logs
            ],
            use_container_width=True,
            hide_index=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
