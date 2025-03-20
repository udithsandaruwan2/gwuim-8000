import calendar
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LeaveRequest, MonthlyLeaveSummary
from datetime import date, timedelta

def get_days_in_month(year, month):
    """Returns the number of days in the month for a given year and month."""
    return calendar.monthrange(year, month)[1]

def update_monthly_summary(instance, change):
    """Updates the monthly leave summary based on leave request changes."""
    if instance.status != 'approved':  # Only process approved requests
        return
    
    start_date = instance.start_date
    coming_date = instance.coming_date
    total_leave_days = instance.total_days  # Total leave days for the request

    # For multi-month leave, distribute the leave days across the months
    while start_date <= coming_date:
        year, month = start_date.year, start_date.month
        month_days = get_days_in_month(year, month)

        # Fetch or create summary record for the current month and leave type
        summary, created = MonthlyLeaveSummary.objects.get_or_create(
            employee=instance.employee,
            year=year,
            month=month,
            request_type=instance.request_type,
            defaults={'total_days': Decimal(0)}
        )

        # Update the total leave days for this month
        if change == 'add':
            summary.total_days += Decimal(total_leave_days)
        elif change == 'remove':
            summary.total_days -= Decimal(total_leave_days)

        summary.save()

        # Move to the next month
        start_date = start_date.replace(day=1) + timedelta(days=month_days)

@receiver(post_save, sender=LeaveRequest)
def handle_leave_request_save(sender, instance, created, **kwargs):
    """
    Signal triggered when a LeaveRequest is created or updated.
    """
    if created:
        update_monthly_summary(instance, 'add')
    else:
        old_instance = LeaveRequest.objects.get(uid=instance.uid)
        if old_instance.status == 'approved' and instance.status != 'approved':
            # If the status was approved and is now not approved, remove the leave
            update_monthly_summary(old_instance, 'remove')
        elif instance.status == 'approved' and old_instance.status != 'approved':
            # If the status is now approved, add the leave
            update_monthly_summary(instance, 'add')

@receiver(post_delete, sender=LeaveRequest)
def handle_leave_request_delete(sender, instance, **kwargs):
    """
    Signal triggered when a LeaveRequest is deleted.
    """
    update_monthly_summary(instance, 'remove')
