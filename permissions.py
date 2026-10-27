"""Role-based permissions enforced in backend services."""

from __future__ import annotations

from models.constants import Role


class PermissionDenied(PermissionError):
    """Raised when a user lacks permission for an action."""


def require_role(user_role: str, allowed: set[Role]) -> None:
    try:
        role = Role(user_role)
    except ValueError as exc:
        raise PermissionDenied("Unknown role.") from exc
    if role not in allowed:
        raise PermissionDenied("You do not have permission for this action.")


def can_manage_users(role: str) -> bool:
    return role == Role.ADMINISTRATOR


def can_delete_patient(role: str) -> bool:
    return role == Role.ADMINISTRATOR


def can_edit_patient(role: str) -> bool:
    return role in {Role.ADMINISTRATOR, Role.RECEPTIONIST}


def can_view_medical_records(role: str) -> bool:
    return role in {Role.ADMINISTRATOR, Role.DOCTOR}


def can_create_medical_record(role: str) -> bool:
    return role in {Role.ADMINISTRATOR, Role.DOCTOR}


def can_manage_doctors(role: str) -> bool:
    return role == Role.ADMINISTRATOR


def can_manage_appointments(role: str) -> bool:
    return role in {Role.ADMINISTRATOR, Role.RECEPTIONIST, Role.DOCTOR}


def can_update_appointment_status(role: str) -> bool:
    return role in {Role.ADMINISTRATOR, Role.DOCTOR, Role.RECEPTIONIST}
