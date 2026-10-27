import streamlit as st

from auth import set_session_user
from database import get_shared_database
from services.user_service import authenticate


def render() -> None:
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] { display: none !important; }
            .block-container {
                max-width: 980px !important;
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
            }
            div[data-testid="stForm"] {
                background: #ffffff;
                border: 1px solid #e8edf3;
                border-radius: 18px;
                padding: 1.25rem 1.25rem 0.5rem;
                box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
            }
            .login-hero {
                background: linear-gradient(135deg, #1d4ed8 0%, #0ea5e9 100%);
                border-radius: 20px;
                padding: 2rem 1.75rem;
                color: #fff;
                min-height: 420px;
            }
            .login-hero h1 { color: #fff; font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem; }
            .login-hero p { color: rgba(255,255,255,0.92); line-height: 1.55; }
            .login-hero .pill {
                display: inline-block;
                background: rgba(255,255,255,0.15);
                border-radius: 999px;
                padding: 0.35rem 0.75rem;
                font-size: 0.78rem;
                margin-top: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="login-hero">
                <h1>CareSync HMS</h1>
                <p>Distributed Healthcare Data Management System for your final-year project demo.</p>
                <p>Secure roles, MongoDB analytics, multi-facility sync, and audit trails — fictional data only.</p>
                <span class="pill">Educational prototype · Not for real clinical use</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="login-card" style="text-align:left;margin-bottom:0.75rem;">
                <div class="login-title" style="font-size:1.35rem;">Sign in</div>
                <div class="login-subtitle">Use your staff account to access the dashboard.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        db_error = st.session_state.get("_db_error")
        if db_error:
            st.error(db_error)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign in to dashboard", use_container_width=True)

        if submitted:
            db = get_shared_database()
            user = authenticate(db, username, password)
            if user is None:
                st.error("Invalid username or password.")
            else:
                set_session_user(user)
                st.rerun()

        st.markdown(
            '<div class="login-hint">Demo after seed: <code>admin</code>, <code>dr.morgan</code>, '
            "<code>reception</code> — password <code>Demo@2026!</code></div>",
            unsafe_allow_html=True,
        )
