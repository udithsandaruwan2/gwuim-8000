from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Employee, LeaveType, LeaveRequest
from audit_logs.utils import create_audit_log
from django.utils import timezone

@receiver(post_save, sender=Employee)
def set_default_leave_balance(sender, instance, created, **kwargs):
    """Set default leave balance when a new employee is created."""
    if created and not instance.leave_balance:
        leave_types = LeaveType.objects.all()
        if leave_types.exists():
            leave_balance = {leave.name.lower(): float(leave.max_days) for leave in leave_types}
            Employee.objects.filter(id=instance.id).update(leave_balance=leave_balance)

            # Log the action: Default leave balance set for new employee
            create_audit_log(
                action_performed="Set Default Leave Balance",
                performed_by=instance.profile,  # Assuming the employee has a profile with this info
                details=f"Set default leave balance for employee {instance.full_name} ({instance.employee_code})"
            )


@receiver(post_save, sender=LeaveType)
def update_employee_leave_balance(sender, instance, created, **kwargs):
    """Update employee leave balances when a new leave type is added."""
    if created:
        employees = Employee.objects.all()
        for employee in employees:
            if employee.leave_balance is None:
                employee.leave_balance = {}
            if instance.name.lower() not in employee.leave_balance:
                employee.leave_balance[instance.name.lower()] = float(instance.max_days)
                employee.save(update_fields=['leave_balance'])

                # Log the action: New leave type added to employee's leave balance
                create_audit_log(
                    action_performed="Updated Employee Leave Balance",
                    performed_by=instance.profile,  # Assuming the leave type has a profile info
                    details=f"Added leave type {instance.name} to employee {employee.full_name} ({employee.employee_code})"
                )


@receiver(post_save, sender=LeaveRequest)
def update_employee_leave_balance_on_request(sender, instance, created, **kwargs):
    """Update employee leave balance when a new leave request is created."""
    if created:
        employee = instance.employee
        leave_type = instance.leave_type
        if leave_type.name.lower() in employee.leave_balance:
            if instance.entering_type == 'manual':
                employee.leave_balance[leave_type.name.lower()] -= instance.manual_total_days
            else:
                employee.leave_balance[leave_type.name.lower()] -= instance.total_days
            employee.save(update_fields=['leave_balance'])

            # Log the action: Leave request created, balance updated
            create_audit_log(
                action_performed="Updated Leave Balance",
                performed_by=instance.employee.profile,  # Assuming the employee has a profile info
                details=f"Updated leave balance for employee {employee.full_name} ({employee.employee_code}) due to leave request"
            )


@receiver(post_delete, sender=LeaveRequest)
def update_employee_leave_balance_on_request(sender, instance, **kwargs):
    """Update employee leave balance when a leave request is deleted."""
    employee = instance.employee
    leave_type = instance.leave_type
    if leave_type.name.lower() in employee.leave_balance:
        employee.leave_balance[leave_type.name.lower()] += instance.total_days
        employee.save(update_fields=['leave_balance'])

        # Log the action: Leave request deleted, balance restored
        create_audit_log(
            action_performed="Restored Leave Balance",
            performed_by=instance.employee.profile,  # Assuming the employee has a profile info
            details=f"Restored leave balance for employee {employee.full_name} ({employee.employee_code}) due to deleted leave request"
        )
