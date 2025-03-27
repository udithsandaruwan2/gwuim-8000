from .models import Employee, LeaveRequest, LeaveType
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import Decimal
from .utils import create_audit_log  # Import the audit log function


def searchEmployees(request):
    search_query = request.GET.get('search', '')

    employees = Employee.objects.distinct().filter(
        Q(employee_code__icontains=search_query) |
        Q(full_name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(position__icontains=search_query) |
        Q(department__name__icontains=search_query)
    )

    # Log the search action
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Searched Employees",
            performed_by=request.user.profile,
            details=f"Searched employees with query: {search_query}"
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

    # Log the pagination action
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Paginated Employees",
            performed_by=request.user.profile,
            details=f"Paginated employees to page {page} with {results} results per page"
        )

    return custom_range, employees


def create_leave_type_arrays_from_model():
    # Fetch all leave types from the database
    leave_types = LeaveType.objects.all()

    # Prepare a dictionary to hold arrays for each leave type
    leave_type_arrays = {}

    # For each leave type, create a separate array
    for leave_type in leave_types:
        # Initialize the array with 12 zeros (for 12 months)
        leave_type_arrays[leave_type.name] = [0] * 12  # Array with 12 months, each initialized to 0

    # Log the creation of leave type arrays
    create_audit_log(
        action_performed="Created Leave Type Arrays",
        performed_by=None,  # This could be anonymous if this function is called by the system
        details="Created leave type arrays for each leave type in the system"
    )

    return leave_type_arrays


def data_insertion_to_arrays(request, employee):
    leave_type_arrays = create_leave_type_arrays_from_model()

    # Iterate over each leave type and their corresponding array
    for leave_type, array in leave_type_arrays.items():
        # Fetch leave requests for the current leave type
        leaves_data = LeaveRequest.objects.filter(leave_type__name=leave_type, employee=employee)

        for leave in leaves_data:
            # Ensure that start_date is a datetime object
            month = leave.start_date.month
            
            if 1 <= month <= 12:
                # Add the total leave days for the corresponding month
                array[month - 1] += leave.total_days

        # Log the data insertion action
        create_audit_log(
            action_performed="Inserted Data into Arrays",
            performed_by=request.user.profile if request.user.is_authenticated else None,
            details=f"Inserted leave data for employee: {employee.full_name} (Employee Code: {employee.employee_code})"
        )

    return leave_type_arrays


def arrays_to_table(request, employee):
    leave_type_arrays = data_insertion_to_arrays(request, employee)

    # Prepare data for rendering
    table_data = []

    # Iterate over each leave type and their corresponding array
    for leave_type, array in leave_type_arrays.items():
        # Store leave_type.name and array (total days per month) in a row
        table_data.append({
            'leave_type_name': leave_type,
            'leave_days_array': array
        })

    # Log the table data creation action
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Generated Leave Data Table",
            performed_by=request.user.profile,
            details=f"Generated leave data table for employee: {employee.full_name} (Employee Code: {employee.employee_code})"
        )

    return table_data


def calculate_total_days(request, request_type, start_date, coming_date):
    """Calculate the total number of leave days."""
    if start_date and coming_date:
        days = (coming_date - start_date).days + 1  # Add 1 to include start date
        total_days = Decimal(max(days - 0.5, 0)) if request_type == 'half' else Decimal(days)

        # Log the total days calculation action
        if request.user.is_authenticated:
            create_audit_log(
                action_performed="Calculated Leave Days",
                performed_by=request.user.profile,
                details=f"Calculated total leave days: {total_days} for request type: {request_type} (Start Date: {start_date}, Coming Date: {coming_date})"
            )

        return total_days
    return Decimal(0)
