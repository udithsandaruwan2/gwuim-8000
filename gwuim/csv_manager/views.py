from django.shortcuts import render, redirect
from .forms import EmployeeFileForm
from .utils import csv_reader
from employees.models import Employee  # Import the Employee model
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests

@login_required(login_url='login')
def importExport(request):
    page = 'csv_manager'
    page_title = 'CSV Manager'

    try:
        profile = request.user.profile
    except:
        profile = None

    if request.method == 'POST' and request.FILES:
        form = EmployeeFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the form (which saves the file)
            file_path = form.instance.file.url  # Get the relative file URL
            csv_reader(file_path)  # Pass the relative URL to the CSV reader
            messages.success(request, 'File imported successfully!')
            return redirect('csv_manager')  # Redirect to 'csv_manager' page after saving
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = EmployeeFileForm()  # Initialize the form for GET request
        

    context = {
        'page': page,
        'page_title': page_title,
        'form': form,
        'profile': profile,
    }

    return render(request, 'csv_manager/import-export.html', context)

@login_required
def export_employees_csv(request):
    # Create the HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Define the header row
    writer.writerow([
        "Employee Code", "Full Name", "Email", "Contact Number", 
        "Date of Birth", "Gender", "Address", "Date of Joining", 
        "Date of Leaving", "Position", "Department", "Leave Balance", 
        "UID", "Created At", "Updated At"
    ])
    
    # Fetch all employees
    employees = Employee.objects.all()

    for emp in employees:
        writer.writerow([
            emp.employee_code if emp.employee_code else "",
            emp.full_name,
            emp.email if emp.email else "",
            emp.contact_number if emp.contact_number else "",
            emp.date_of_birth if emp.date_of_birth else "",
            emp.gender if emp.gender else "",
            emp.address if emp.address else "",
            emp.date_of_joining if emp.date_of_joining else "",
            emp.date_of_leaving if emp.date_of_leaving else "",
            emp.position if emp.position else "",
            emp.department.name if emp.department else "",
            emp.leave_balance if emp.leave_balance else "{}",
            emp.uid,
            emp.created_at,
            emp.updated_at
        ])

    return response

API_BASE_URL = 'http://localhost:8001/api/'

@login_required(login_url='login')
def teaCardSheet(request):
    page = 'tea_card_sheet'
    page_title = 'Tea Card Sheet'
    year = request.GET.get('year')
    month = request.GET.get('month')

    try:
        profile = request.user.profile
    except AttributeError:
        profile = None

    employees = Employee.objects.filter(is_teacard_holder=True)

    attendance_data = []

    for employee in employees:
        employee_code = employee.employee_code
        employee_name = employee.full_name

        if not employee_code:
            messages.error(request, f'Employee {employee.full_name} does not have an employee code.')
            continue

        try:
            response = requests.get(
                f'{API_BASE_URL}employees/{employee_code}/{year}/{month}', 
                timeout=5
            )
            response.raise_for_status()
            count = response.json()

            attendance_data.append({
                'id': employee_code,
                'name': employee_name,
                'attendance_count': count,
            })
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error fetching data for {employee_name} ({employee_code}): {e}')

    attendance_data = sorted(attendance_data, key=lambda x: x['id'])
    left_table = attendance_data[:35]
    right_table = attendance_data[35:]


    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile,
        'year': year,
        'month': month,
        'attendance_data': attendance_data,
        'left_table': left_table,
        'right_table': right_table,
    }

    return render(request, 'csv_manager/tea-card-sheet.html', context)


@login_required(login_url='login')
def teaCardExportSelector(request):
    page = 'tea_card_sheet'
    page_title = 'Tea Card Sheet'

    try:
        profile = request.user.profile
    except:
        profile = None

    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile,
    }

    return render(request, 'csv_manager/tea-card-exporter.html', context)