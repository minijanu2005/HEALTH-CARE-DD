import streamlit as st

from auth import require_login
from database import get_shared_database
from services.audit_service import list_audit_logs
from ui.components import begin_panel, end_panel, page_intro


def render() -> None:
    user = require_login()
    db = get_shared_database()

    page_intro("Audit logs", "Security and administrative events — no passwords or secrets stored.")

    begin_panel("Activity log", "Filter by action type")
    action = st.selectbox(
        "Filter by action",
        [
            "",
            "login_success",
            "login_failed",
            "logout",
            "create_patient",
            "update_patient",
            "create_user",
            "create_medical_record",
            "view_medical_record",
        ],
        label_visibility="collapsed",
    )
    try:
        logs = list_audit_logs(db, actor_role=user["role"], action=action or None, limit=200)
    except PermissionError as exc:
        st.error(str(exc))
        end_panel()
        return

    st.dataframe(
        [
            {
                "Timestamp": log.get("timestamp"),
                "User": log.get("actor_username"),
                "Role": log.get("actor_role"),
                "Action": log.get("action"),
                "Entity": f"{log.get('entity_type')}:{log.get('entity_id')}",
            }
            for log in logs
        ],
        use_container_width=True,
        hide_index=True,
    )
    end_panel()
