from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, LeaveType, LeaveRequest
from .utils import searchEmployees, paginateEmployees, calculate_total_days, arrays_to_table
from audit_logs.utils import create_audit_log
from .forms import EmployeeForm, LeaveTypeForm
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib import messages
from users.models import Profile

@login_required(login_url='login')
def employee(request, pk):

    try:
        employee = Employee.objects.get(uid=pk)
    except:
        employee = None
        messages.error(request, 'Employee not found.')
        return redirect('employees')

    try:
        profile = Profile.objects.get(employee=employee)
    except:
        profile = None
        messages.error(request, 'Profile not found.')
        return redirect('employees')

    # Store employee uid in session
    request.session['employee_uid'] = pk

    return redirect('profile', pk=profile.uid)

@login_required(login_url='login')
def employees(request):
    page = 'employees'
    page_title = 'Employees'

    try:
        profile = request.user.profile
    except:
        profile = None

    # Queries With pagination
    employees, search_query = searchEmployees(request)
    custom_range, employees = paginateEmployees(request, employees, 10)
    employee_form = EmployeeForm()

    # Handling POST request for adding new employee
    if request.method == 'POST':
        if request.POST.get('action') == 'addEmployee':
            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                employee_form.save()
                # Log action: Add Employee
                create_audit_log(
                    action_performed="Added Employee",
                    performed_by=request.user.profile,
                    details=f"Added new employee with data: {employee_form.cleaned_data}"
                )
                messages.success(request, 'Employee added successfully.')
                return redirect('employees')
            else:   
                messages.error(request, 'Error adding employee. Please check the form.')
                return redirect('employees')

    context = {
        'page': page,
        'page_title': page_title,
        'employees': employees,
        'search_query': search_query,
        'custom_range': custom_range,
        'employee_form': employee_form,
        'profile': profile
    }
    return render(request, 'employees/employees.html', context)


@login_required(login_url='login')
def employeeIndetail(request, pk):
    page = 'employees'
    page_title = 'Employee Details'

    try:
        profile = request.user.profile
        print(profile)
    except:
        profile = None

    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    current_year = timezone.now().year
    employee = Employee.objects.get(uid=pk)
    leave_types = LeaveType.objects.all()

    leaves_data = arrays_to_table(request, employee)

    # Handling POST request for adding a leave request
    if request.method == 'POST':
        if request.POST.get('action') == 'addLeaveRequest':
            leave_type = LeaveType.objects.get(uid=request.POST.get('leaveType'))
            request_type = request.POST.get('requestType')
            start_date = timezone.datetime.strptime(request.POST.get('startDate'), '%Y-%m-%d').date()
            comming_date = timezone.datetime.strptime(request.POST.get('commingDate'), '%Y-%m-%d').date()
            leave_balance = employee.leave_balance[f'{leave_type.name.lower()}']
            total_days = calculate_total_days(request_type, start_date, comming_date)
            entering_type = request.POST.get('leaveEnteringType')
            manual_total_days = request.POST.get('manualTotalDays')
            if not manual_total_days:
                manual_total_days = 0.0
            manual_total_days = float(manual_total_days)

            if total_days <= leave_balance or manual_total_days <= leave_balance:
                reason = request.POST.get('reason')
                status = request.POST.get('status')
                # Create leave request and log it
                leave_request = LeaveRequest.objects.create(
                    employee=employee,
                    systemized_by=profile,
                    reason=reason,
                    status=status,
                    leave_type=leave_type,
                    start_date=start_date,
                    coming_date=comming_date,
                    request_type=request_type,
                    entering_type=entering_type,
                    manual_total_days=manual_total_days
                )
                # Log action: Add Leave Request
                create_audit_log(
                    action_performed="Added Leave Request",
                    performed_by=request.user.profile,
                    details=f"Leave request added for employee {employee.full_name} ({employee.employee_code})"
                )
                messages.success(request, 'Leave request submitted successfully.')
            else:
                messages.error(request, f'Insufficient leave balance in {leave_type}.')
            
        return redirect('employee-indetail', pk=pk)

    context = {
        'page': page,
        'page_title': page_title,
        'pk': pk,
        'current_year': current_year,
        'employee': employee,
        'profile': profile,
        'leave_types': leave_types,
        'months': months,
        'leaves_data': leaves_data
    }

    return render(request, 'employees/employee-indetail.html', context)


@login_required(login_url='login')
def employeeLeaveHistory(request, pk):
    page = 'employee_leave_history'
    page_title = 'Employee Leave History'

    try:
        profile = request.user.profile
    except:
        profile = None

    # Fetch leave requests for the employee with the given primary key
    leave_requests = LeaveRequest.objects.filter(employee__uid=pk)

    # Log action: View Leave History
    create_audit_log(
        action_performed="Viewed Leave History",
        performed_by=request.user.profile,
        details=f"Viewed leave history for employee {pk}"
    )

    context = {
        'page': page,
        'page_title': page_title,
        'leave_requests': leave_requests,
        'pk': pk,
        'profile': profile
    }

    return render(request, 'employees/employee-indetail-leave-request-history.html', context)


def downloadReport(request, pk):
    try:
        # Fetch employee details based on the pk (primary key)
        employee = Employee.objects.get(pk=pk)
        
        # Prepare data to pass into the template
        current_year = timezone.now().year
        
        context = {
            'pk': pk,
            'current_year': current_year,
            'employee': employee,
            'page': 'employee_report',
            'page_title': 'Leave Report for {}'.format(employee.full_name),
            'request': request,  # Pass the request to generate absolute URLs
        }
        
        # Render the HTML content with context
        html_content = render_to_string('employees/employee-indetail.html', context)

        # Create the PDF with WeasyPrint (A4 landscape layout)
        pdf = HTML(string=html_content).write_pdf(
            stylesheets=[
                'static/theme_dashboard/assets/css/styles.css',  # Ensure the CSS path is correct
            ],
            presentational_hints=True,
            options={'page-size': 'A4', 'orientation': 'landscape'}
        )

        # Log action: Download Report
        create_audit_log(
            action_performed="Downloaded Employee Report",
            performed_by=request.user.profile,
            details=f"Downloaded leave report for employee {employee.full_name} ({employee.employee_code})"
        )

        # Return the PDF as a response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=leave_report_{pk}.pdf'
        return response
    except Employee.DoesNotExist:
        # Handle the case where the employee with the given pk does not exist
        return HttpResponse("Employee not found.", status=404)


@login_required(login_url='login')
def leaveTypes(request):
    page = 'leave_types'
    page_title = 'Leave Types'

    try:
        profile = request.user.profile
    except:
        profile = None

    # Handling POST request for adding new leave type
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'addLeaveType':
            code = request.POST.get('leaveTypeCode')
            name = request.POST.get('leaveTypeName')
            max_days = request.POST.get('leaveTypeMaxDays')
            description = request.POST.get('leaveTypeDescription')
            # Create new leave type and log it
            LeaveType.objects.create(code=code, name=name, max_days=max_days, description=description)
            create_audit_log(
                action_performed="Added Leave Type",
                performed_by=request.user.profile,
                details=f"Added new leave type with code: {code} and name: {name}"
            )

            messages.success(request, 'Leave type added successfully.')
            return redirect('leave_types')

    leave_types = LeaveType.objects.all()

    context = {
        'page': page,
        'page_title': page_title,
        'leave_types': leave_types,
        'profile': profile
    }

    return render(request, 'employees/leave-types.html', context)


@login_required(login_url='login')
def updateLeaveType(request, pk):
    page = 'update_leave_type'
    page_title = 'Update Leave Type'

    try:
        profile = request.user.profile
    except:
        profile = None

    leave_type = get_object_or_404(LeaveType, uid=pk)  # Ensures object exists
    form = LeaveTypeForm(instance=leave_type)  # Prefill form with existing data

    # Handling POST request for updating leave type
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            # Log action: Update Leave Type
            create_audit_log(
                action_performed="Updated Leave Type",
                performed_by=request.user.profile,
                details=f"Updated leave type {leave_type.name} with new data: {form.cleaned_data}"
            )
            messages.success(request, 'Leave type updated successfully.')
            return redirect('leave_types')
        else:
            messages.error(request, 'Error updating leave type. Please check the form.')
            return redirect('leave_types')

    context = {
        'page': page,
        'page_title': page_title,
        'leave_type': leave_type,  # Pass object to template for display
        'form': form,
        'profile': profile
    }

    return render(request, 'employees/update-leave-type.html', context)


@login_required(login_url='login')
def deleteLeaveTypeConfirmation(request, pk):
    page = 'delete_leave_type'
    page_title = 'Delete Leave Type'

    try:
        profile = request.user.profile
    except:
        profile = None

    leave_type = get_object_or_404(LeaveType, uid=pk)  # Ensures object exists

    if request.method == 'POST':
        leave_type.delete()
        # Log action: Delete Leave Type
        create_audit_log(
            action_performed="Deleted Leave Type",
            performed_by=request.user.profile,
            details=f"Deleted leave type {leave_type.name} (Code: {leave_type.code})"
        )

        messages.success(request, 'Leave type deleted successfully.')
        return redirect('leave_types')  # Redirect after successful deletion

    context = {
        'page': page,
        'page_title': page_title,
        'leave_type': leave_type,  # Pass object to template for display
        'profile': profile
    }

    return render(request, 'dashboard/delete-confirmation.html', context)
