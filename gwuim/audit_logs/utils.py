# utils.py
from .models import AuditLog
from django.utils.timezone import now

def create_audit_log(action_performed, performed_by, details):
    """Create a new audit log record."""
    audit_log = AuditLog(
        action_performed=action_performed,
        performed_by=performed_by,
        details=details,
        created_at=now(),  # use current time
        updated_at=now()
    )
    audit_log.save()
    return audit_log
