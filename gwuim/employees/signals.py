from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Employee, LeaveType, LeaveRequest
from audit_logs.utils import create_audit_log
from django.utils import timezone
from users.models import Profile
from .models import Employee

@receiver(post_save, sender=Employee)
def set_default_leave_balance(sender, instance, created, **kwargs):
    """Set default leave balance when a new employee is created."""
    if created and not instance.leave_balance:
        leave_types = LeaveType.objects.all()
        if leave_types.exists():
            leave_balance = {leave.name.lower(): float(leave.max_days) for leave in leave_types}
            Employee.objects.filter(uid=instance.uid).update(leave_balance=leave_balance)



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


@receiver(post_delete, sender=LeaveRequest)
def update_employee_leave_balance_on_request(sender, instance, **kwargs):
    """Update employee leave balance when a leave request is deleted."""
    employee = instance.employee
    leave_type = instance.leave_type
    if leave_type.name.lower() in employee.leave_balance:
        employee.leave_balance[leave_type.name.lower()] += instance.total_days
        employee.save(update_fields=['leave_balance'])

@receiver(post_save, sender=Employee)
def createProfile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            employee=instance, 
            username=instance.employee_code,
            email=instance.email,
            full_name=instance.full_name, 
        )

@receiver(post_save, sender=Profile)
def updateUser(sender, instance, created, **kwargs):
    if not created:
        employee = instance.employee
        employee.employee_code= instance.username
        employee.full_name = instance.full_name
        employee.email = instance.email
        employee.save()

@receiver(post_delete, sender=Profile)
def deleteUser(sender, instance, **kwargs):
    employee = instance.employee
    employee.delete()