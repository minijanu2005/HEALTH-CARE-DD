import streamlit as st

from auth import require_login
from database import get_shared_database
from models.constants import Role
from permissions import can_manage_users
from services.user_service import create_user, list_users, set_user_active
from ui.components import begin_panel, end_panel, page_intro
from utils.validators import ValidationError


def render() -> None:
    user = require_login()
    if not can_manage_users(user["role"]):
        st.error("Administrators only.")
        return

    db = get_shared_database()
    actor = {"username": user["username"], "role": user["role"]}

    page_intro("Administration", "Manage staff accounts, roles, and activation status.")

    begin_panel("User directory", "All system accounts")
    users = list_users(db)
    st.dataframe(
        [
            {
                "Username": u["username"],
                "Name": u.get("full_name"),
                "Role": u.get("role"),
                "Active": u.get("active", True),
            }
            for u in users
        ],
        use_container_width=True,
        hide_index=True,
    )
    end_panel()

    c1, c2 = st.columns(2)
    with c1:
        begin_panel("Create user", "Minimum password length: 8 characters")
        with st.form("create_user"):
            username = st.text_input("Username *")
            full_name = st.text_input("Full name *")
            password = st.text_input("Password *", type="password")
            role = st.selectbox("Role", [r.value for r in Role])
            if st.form_submit_button("Create user", use_container_width=True):
                try:
                    create_user(
                        db,
                        actor=actor,
                        username=username,
                        password=password,
                        role=role,
                        full_name=full_name,
                    )
                    st.success("User created.")
                    st.rerun()
                except (ValidationError, PermissionError) as exc:
                    st.error(str(exc))
        end_panel()
    with c2:
        begin_panel("Activate / deactivate", "Instantly disable login without deleting history")
        target = st.selectbox("User", [u["username"] for u in users])
        new_state = st.radio("Status", ["Active", "Inactive"], horizontal=True)
        if st.button("Update account status", use_container_width=True):
            try:
                set_user_active(db, actor=actor, username=target, active=new_state == "Active")
                st.success("Updated.")
                st.rerun()
            except (ValidationError, PermissionError) as exc:
                st.error(str(exc))
        end_panel()
