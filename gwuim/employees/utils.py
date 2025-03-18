from .models import Employee
from django.db.models import Q
from .models import LeaveRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.utils.timezone import now
from datetime import date, timedelta

def searchEmployees(request):
    search_query = request.GET.get('search', '')

    employees = Employee.objects.distinct().filter(
        Q(employee_code__icontains=search_query) |
        Q(full_name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(position__icontains=search_query) |
        Q(department__name__icontains=search_query) 
    )
    
    return employees, search_query

def paginateEmployees(request, employees, results):
    page = request.GET.get('page')
    paginator = Paginator(employees, results)

    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        employees = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        employees = paginator.page(page)

    left_index = max(int(page) - 1, 1)
    right_index = min(int(page) + 2, paginator.num_pages + 1)

    custom_range = range(left_index, right_index)
    return custom_range, employees


def get_monthly_leave(employee, year=None, month=None):
    if not year or not month:
        today = now().date()
        year, month = today.year, today.month

    # First and last day of the given month
    first_day_of_month = date(year, month, 1)
    last_day_of_month = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)

    # Get all leave requests that overlap with the given month
    leave_requests = LeaveRequest.objects.filter(
        employee=employee,
        status='approved',
        start_date__lte=last_day_of_month,  # Started before or within the month
        coming_date__gte=first_day_of_month,  # Ends after or within the month
    )

    total_days = 0

    for leave in leave_requests:
        # Get the actual start and end for this month
        effective_start = max(leave.start_date, first_day_of_month)
        effective_end = min(leave.coming_date, last_day_of_month)

        days_in_month = (effective_end - effective_start).days + 1  # Inclusive of both days
        
        if leave.request_type == 'half':
            total_days += days_in_month - 0.5
        else:
            total_days += days_in_month

    return total_days

