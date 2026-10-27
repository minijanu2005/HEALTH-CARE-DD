from models.constants import Role
from permissions import (
    PermissionDenied,
    can_create_medical_record,
    can_delete_patient,
    can_edit_patient,
    require_role,
)


def test_receptionist_cannot_delete_patient() -> None:
    assert can_delete_patient(Role.RECEPTIONIST) is False


def test_admin_can_delete_patient() -> None:
    assert can_delete_patient(Role.ADMINISTRATOR) is True


def test_doctor_can_create_records() -> None:
    assert can_create_medical_record(Role.DOCTOR) is True


def test_receptionist_cannot_view_records() -> None:
    assert can_create_medical_record(Role.RECEPTIONIST) is False


def test_require_role_denies() -> None:
    try:
        require_role(Role.RECEPTIONIST, {Role.ADMINISTRATOR})
        assert False, "expected PermissionDenied"
    except PermissionDenied:
        pass


def test_receptionist_can_edit_patient() -> None:
    assert can_edit_patient(Role.RECEPTIONIST) is True
