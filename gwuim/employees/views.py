from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Employee

@login_required(login_url='login')
def employees(request):
    page = 'employees'
    page_title = 'Employees'

    # Queries
    employees = Employee.objects.all()

    context = {
        'page': page,
        'page_title': page_title,
        'employees': employees
    }
    return render(request, 'employees/employees.html', context)
