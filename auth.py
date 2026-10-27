"""Password hashing and Streamlit session helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypedDict

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from config import get_settings

_ph = PasswordHasher()


class SessionUser(TypedDict):
    username: str
    role: str
    full_name: str
    user_id: str


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(password_hash: str, plain: str) -> bool:
    try:
        return _ph.verify(password_hash, plain)
    except VerifyMismatchError:
        return False


def get_session_user() -> SessionUser | None:
    import streamlit as st

    user = st.session_state.get("user")
    if not user:
        return None
    expires_at = st.session_state.get("session_expires_at")
    if expires_at and datetime.now(timezone.utc).timestamp() > float(expires_at):
        clear_session_user()
        return None
    return user  # type: ignore[return-value]


def set_session_user(user_doc: dict[str, Any]) -> None:
    import streamlit as st

    settings = get_settings()
    st.session_state["user"] = SessionUser(
        username=user_doc["username"],
        role=user_doc["role"],
        full_name=user_doc.get("full_name", user_doc["username"]),
        user_id=str(user_doc["_id"]),
    )
    st.session_state["session_expires_at"] = (
        datetime.now(timezone.utc).timestamp() + settings.session_timeout_minutes * 60
    )


def clear_session_user() -> None:
    import streamlit as st

    user = st.session_state.get("user")
    if user:
        try:
            from database import get_shared_database
            from utils.audit import log_audit

            log_audit(
                get_shared_database(),
                actor_username=user["username"],
                actor_role=user["role"],
                action="logout",
                entity_type="user",
                entity_id=user["username"],
            )
        except Exception:
            pass
    st.session_state.pop("user", None)
    st.session_state.pop("session_expires_at", None)


def require_login() -> SessionUser:
    user = get_session_user()
    if user is None:
        import streamlit as st

        st.warning("Please log in to continue.")
        st.stop()
    return user
