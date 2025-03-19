from django import template
from employees.models import LeaveType  # Import your model

register = template.Library()

@register.filter
def get_leave_name(uid):
    """Fetch leave name from the database using UID."""
    leave_type = LeaveType.objects.filter(uid=uid).first()
    return leave_type.name if leave_type else "Unknown Leave Type"
