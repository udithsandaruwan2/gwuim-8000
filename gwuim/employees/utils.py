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

    # Dictionary to store leave days based on leave type
    leave_summary = {}
    

    for leave in leave_requests:
        request_type = leave.request_type # e.g., 'full', 'half', 'sick', etc.
        leave_type = leave.leave_type.uid
        if leave_type and request_type not in leave_summary:
            leave_summary[leave_type] = 0
        else:
            leave_summary[leave_type] += leave.total_days


    return leave_summary

def get_yearly_leave(employee, year=None):
    if not year:
        year = now().year

    yearly_leaves = {month: get_monthly_leave(employee, year, month) for month in range(1, 13)}

    return yearly_leaves


def process_leave_data(data):
    # Step 1: Identify all unique leave types
    leave_types = set()
    for month_data in data.values():
        leave_types.update(month_data.keys())

    # Step 2: Create dynamically named arrays for each leave type (initialized with 0 for 12 months)
    leave_balances = {leave_type: [0] * 12 for leave_type in leave_types}

    # Step 3: Populate leave balances for each month
    for month in range(1, 13):  # Ensure all months are processed
        inner_dict = data.get(month, {})  # Get data for the month or an empty dict
        for leave_type in leave_types:
            leave_balances[leave_type][month - 1] = inner_dict.get(leave_type, 0)  # Default to 0 if empty

    return leave_balances  # Returns a dictionary of dynamically generated arrays
