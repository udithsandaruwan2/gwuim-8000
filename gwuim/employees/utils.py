from .models import Employee
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import LeaveType, LeaveRequest
from decimal import Decimal
from datetime import datetime, timedelta


def searchEmployees(request):
    search_query = request.GET.get('search', '')
    employees = Employee.objects.distinct().filter(
        Q(employee_code__icontains=search_query) |
        Q(full_name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(designation__name__icontains=search_query) |
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


def create_leave_type_arrays_from_model():
    # Fetch all leave types from the database
    leave_types = LeaveType.objects.all()

    # Prepare a dictionary to hold arrays for each leave type
    leave_type_arrays = {}

    # For each leave type, create a separate array
    for leave_type in leave_types:
        # Initialize the array with 12 zeros (for 12 months)
        leave_type_arrays[leave_type.name] = [0] * 12  # Array with 12 months, each initialized to 0

    return leave_type_arrays

from datetime import datetime, timedelta
from collections import defaultdict

def data_insertion_to_arrays(request, employee):
    leave_type_arrays = create_leave_type_arrays_from_model()

    for leave_type, array in leave_type_arrays.items():
        leaves_data = LeaveRequest.objects.filter(leave_type__name=leave_type, employee=employee)

        for leave in leaves_data:
            start_date = leave.start_date if isinstance(leave.start_date, datetime) else datetime.strptime(str(leave.start_date), "%Y-%m-%d")
            coming_date = leave.coming_date if isinstance(leave.coming_date, datetime) else datetime.strptime(str(leave.coming_date), "%Y-%m-%d")

            if leave.manual_total_days:
                array[start_date.month - 1] += leave.manual_total_days
            else:
                current_date = start_date
                while current_date <= coming_date:
                    month_index = current_date.month - 1
                    end_of_month = datetime(current_date.year, current_date.month % 12 + 1, 1) - timedelta(days=1)
                    if coming_date <= end_of_month:
                        array[month_index] += (coming_date - current_date).days
                        break
                    else:
                        array[month_index] += (end_of_month - current_date).days + 1
                        current_date = end_of_month + timedelta(days=1)

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
    return table_data

def calculate_total_days(request_type, start_date, coming_date):
        """Calculate the total number of leave days."""
        if start_date and coming_date:
            days = (coming_date - start_date).days + 1  # Add 1 to include start date
            return Decimal(max(days - 0.5, 0)) if request_type == 'half' else Decimal(days)
        return Decimal(0)