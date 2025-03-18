from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Employee
from .utils import searchEmployees, paginateEmployees

@login_required(login_url='login')
def employees(request):
    page = 'employees'
    page_title = 'Employees'

    # Queries With pagination
    employees, search_query = searchEmployees(request)
    custom_range, employees = paginateEmployees(request, employees, 10)
    context = {
        'page': page,
        'page_title': page_title,
        'employees': employees,
        'search_query': search_query,
        'custom_range': custom_range
    }
    return render(request, 'employees/employees.html', context)
