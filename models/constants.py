"""Shared constants for roles, statuses, and collection names."""

from enum import StrEnum


class Role(StrEnum):
    ADMINISTRATOR = "Administrator"
    DOCTOR = "Doctor"
    RECEPTIONIST = "Receptionist"


class AppointmentStatus(StrEnum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No-show"


class SyncStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"


class Collection(StrEnum):
    USERS = "users"
    PATIENTS = "patients"
    DOCTORS = "doctors"
    APPOINTMENTS = "appointments"
    MEDICAL_RECORDS = "medical_records"
    AUDIT_LOGS = "audit_logs"
    COUNTERS = "counters"
    SYNC_OUTBOX = "sync_outbox"
    SYNC_LOG = "sync_log"
    SYNC_PROCESSED = "sync_processed"
    SYNC_CONFLICTS = "sync_conflicts"
