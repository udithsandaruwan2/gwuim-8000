from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Employee, LeaveType, LeaveRequest

@receiver(post_save, sender=Employee)
def set_default_leave_balance(sender, instance, created, **kwargs):
    if created and not instance.leave_balance:
        leave_types = LeaveType.objects.all()
        if leave_types.exists():
            leave_balance = {leave.name.lower(): float(leave.max_days) for leave in leave_types}
            Employee.objects.filter(id=instance.id).update(leave_balance=leave_balance)

@receiver(post_save, sender=LeaveType)
def update_employee_leave_balance(sender, instance, created, **kwargs):
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
    employee = instance.employee
    leave_type = instance.leave_type
    if leave_type.name.lower() in employee.leave_balance:
        employee.leave_balance[leave_type.name.lower()] += instance.total_days
        employee.save(update_fields=['leave_balance'])