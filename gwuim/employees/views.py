from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, LeaveType, LeaveRequest
from .utils import searchEmployees, paginateEmployees, calculate_total_days, arrays_to_table
from audit_logs.utils import create_audit_log
from .forms import EmployeeForm, LeaveTypeForm
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib import messages
from users.models import Profile
import requests
from gwuim.settings import API_BASE_URL

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
def employeeIndetailFromAttendance(request, pk):
    page = 'employees_leave_from_attendance'
    page_title = 'Employee Details'

    try:
        profile = request.user.profile
    except AttributeError:
        profile = None

    current_year = timezone.now().year
    employee = get_object_or_404(Employee, uid=pk)
    leave_days = []

    try:
        response = requests.get(
            f'{API_BASE_URL}employees/{employee.employee_code}/{current_year}/', 
            timeout=5
        )
        response.raise_for_status()
        leave_days = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error fetching employee data: {e}')

    # print(leave_days)

    context = {
        'page': page,
        'page_title': page_title,
        'pk': pk,
        'current_year': current_year,
        'employee': employee,
        'profile': profile,
        'leave_days': leave_days
    }

    return render(request, 'employees/employee-indetail.html', context)


@login_required(login_url='login')
def employeeIndetail(request, pk):
    page = 'employees'
    page_title = 'Employee Details'

    try:
        profile = request.user.profile
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

def get_other_leave_data(request, _id, _year, _month):
    employee_id = _id
    month = _month
    year = _year
    print(f"Fetching other leave data for employee ID: {employee_id}, Year: {year}, Month: {month}")
    
    # Call the external API (optional: handle errors here)
    response = requests.get(
        f'{API_BASE_URL}employees/{employee_id}/{year}/{month}/other-leaves/', 
        timeout=5
    )
    
    # Dummy example: you can pass fetched JSON data to the template if needed
    leave_data = response.json() if response.status_code == 200 else {}
    if leave_data:
        leave_data = leave_data[0]
        late_count = leave_data['late_count']
        late_count_covered = leave_data['late_count_covered']
        short_leave_balance = leave_data['short_leave_balance']
        half_leave_count = leave_data['half_leave_count']
        print(f"Late count for employee {employee_id} in {year}-{month}: {late_count}")
    else:
        late_count = 0
        late_count_covered = 0
        short_leave_balance = 0
        half_leave_count = 0
        print(f"No leave data found for employee {employee_id} in {year}-{month}")

    context = {
        'employee_id': employee_id,
        'year': year,
        'month': month,
        'leave_data': leave_data,  # if you need dynamic values in template
        'late_count': late_count,
        'late_count_covered': late_count_covered,
        'short_leave_balance': short_leave_balance,
        'half_leave_count': half_leave_count,
    }
    return render(request, 'employees/partials/table.html', context)



































# import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Title, Designation
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from audit_logs.utils import create_audit_log

@login_required(login_url='login')
def titles(request):
    page = 'titles'
    page_title = 'Titles'

    try:
        profile = request.user.profile
    except:
        profile = None

    # Log the view page action
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Viewed Titles Page",
            performed_by=request.user.profile,  # Assuming the user has a Profile object
            details="User viewed the titles page."
        )
    titles = Title.objects.all()
    designations = Designation.objects.all()

    # Create a dictionary to map title to their designations
    title_designations = {title.uid: [] for title in titles}
    for designation in designations:
        if designation.title:  # Check if the title is not None
            title_designations[designation.title.uid].append(designation)

    # # Handle POST request for adding faculty or department
    # if request.method == 'POST':
    #     # Handling 'addFaculty' action
    #     if request.POST.get('action') == 'addFaculty':
    #         faculty_code = request.POST.get('facultyCode')
    #         faculty_name = request.POST.get('facultyName')
    #         Faculty.objects.create(code=faculty_code, name=faculty_name)

    #         # Log the action of adding a faculty
    #         if request.user.is_authenticated:
    #             create_audit_log(
    #                 action_performed="Added Faculty",
    #                 performed_by=request.user.profile,
    #                 details=f"Added faculty with code: {faculty_code}, name: {faculty_name}"
    #             )
            
    #         messages.success(request, 'Faculty added successfully.')
    #         return redirect('departments')  # Redirect to refresh the page

    #     # Handling 'addDepartment' action
    #     elif request.POST.get('action') == 'addDepartment':
    #         department_code = request.POST.get('departmentCode')
    #         department_name = request.POST.get('departmentName')
    #         faculty_id = request.POST.get('facultyId')

    #         try:
    #             faculty = Faculty.objects.get(uid=faculty_id)
    #             Department.objects.create(code=department_code, name=department_name, faculty=faculty)

    #             # Log the action of adding a department
    #             if request.user.is_authenticated:
    #                 create_audit_log(
    #                     action_performed="Added Department",
    #                     performed_by=request.user.profile,
    #                     details=f"Added department with code: {department_code}, name: {department_name}, under faculty: {faculty.name}"
    #                 )
    #         except Faculty.DoesNotExist:
    #             messages.error(request, 'Faculty not found.')
    #             return JsonResponse({'success': False, 'error': 'Faculty not found.'})
            
    #         messages.success(request, 'Department added successfully.')
    #         return redirect('departments')  # Redirect to refresh the page

    #     # Handling 'updateDepartments' action for AJAX request
    #     elif request.POST.get('action') == 'updateDepartments':
    #         updated_departments = json.loads(request.POST.get('updatedDepartments'))  # Get the list of updated departments
            
    #         try:
    #             for dept_data in updated_departments:
    #                 department = Department.objects.get(uid=dept_data['uid'])
    #                 old_name = department.name
    #                 department.name = dept_data['name']
    #                 department.save()

    #                 # Log the action of updating a department
    #                 if request.user.is_authenticated:
    #                     create_audit_log(
    #                         action_performed="Updated Department",
    #                         performed_by=request.user.profile,
    #                         details=f"Updated department from name: {old_name} to {department.name}"
    #                     )
    #             messages.success(request, 'Departments updated successfully.')
    #             # Return success response after updating departments
    #             return JsonResponse({'success': True})
    #         except Department.DoesNotExist:
    #             messages.error(request, 'Department not found.')
    #             # Return failure response if the department is not found
    #             return JsonResponse({'success': False, 'error': 'Department not found'})

    context = {
        'page': page,
        'page_title': page_title,
        'titles': titles,
        'title_designations': title_designations,
        'profile': profile
    }
    return render(request, 'employees/titles.html', context)

# @login_required(login_url='login')
# @csrf_exempt  # Use this only if necessary
# def update_departments(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         action = data.get('action')

#         if action == 'updateDepartments':
#             faculty_uid = data.get('facultyUid')
#             updated_departments = data.get('updatedDepartments')

#             try:
#                 faculty = Faculty.objects.get(uid=faculty_uid)

#                 # Update department names
#                 for dept_data in updated_departments:
#                     department = Department.objects.get(uid=dept_data['uid'], faculty=faculty)
#                     old_name = department.name
#                     department.name = dept_data['name']
#                     department.save()

#                     # Log the department update action
#                     if request.user.is_authenticated:
#                         create_audit_log(
#                             action_performed="Updated Department",
#                             performed_by=request.user.profile,
#                             details=f"Updated department from name: {old_name} to {department.name}, under faculty: {faculty.name}"
#                         )
#                 messages.success(request, 'Departments updated successfully.')
#                 return JsonResponse({'success': True})
#             except Faculty.DoesNotExist:
#                 messages.error(request, 'Faculty not found.')
#                 return JsonResponse({'success': False, 'error': 'Faculty not found.'})
#             except Department.DoesNotExist:
#                 messages.error(request, 'Department not found.')
#                 return JsonResponse({'success': False, 'error': 'Department not found.'})
#         messages.error(request, 'Invalid action.')
#         return JsonResponse({'success': False, 'message': 'Invalid action.'})
#     messages.error(request, 'Invalid request method.')
#     return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# @login_required(login_url='login')
# def deleteDepartmentConfirmation(request, pk):
#     page = 'delete_department_type'
#     page_title = 'Delete Department Type'

#     try:
#         profile = request.user.profile
#     except:
#         profile = None

#     department = get_object_or_404(Department, uid=pk)  # Ensures object exists

#     # Log the deletion action (before actually deleting the department)
#     if request.user.is_authenticated:
#         create_audit_log(
#             action_performed="Viewed Department Deletion Confirmation",
#             performed_by=request.user.profile,
#             details=f"User is about to delete department: {department.name} (UID: {department.uid})"
#         )

#     if request.method == 'POST':
#         # Log the department deletion
#         if request.user.is_authenticated:
#             create_audit_log(
#                 action_performed="Deleted Department",
#                 performed_by=request.user.profile,
#                 details=f"Deleted department: {department.name} (UID: {department.uid})"
#             )

#         department.delete()
#         messages.success(request, 'Department deleted successfully.')
#         return redirect('departments')  # Redirect after successful deletion

#     context = {
#         'page': page,
#         'page_title': page_title,
#         'profile': profile
#     }

#     return render(request, 'dashboard/delete-confirmation.html', context)

# @login_required(login_url='login')
# def deleteFacultyConfirmation(request, pk):
#     page = 'delete_faculty'
#     page_title = 'Delete Faculty'

#     try:
#         profile = request.user.profile
#     except:
#         profile = None

#     faculty = get_object_or_404(Faculty, uid=pk)  # Ensures object exists

#     # Log the deletion action (before actually deleting the faculty)
#     if request.user.is_authenticated:
#         create_audit_log(
#             action_performed="Viewed Faculty Deletion Confirmation",
#             performed_by=request.user.profile,
#             details=f"User is about to delete faculty: {faculty.name} (UID: {faculty.uid})"
#         )

#     if request.method == 'POST':
#         # Log the faculty deletion
#         if request.user.is_authenticated:
#             create_audit_log(
#                 action_performed="Deleted Faculty",
#                 performed_by=request.user.profile,
#                 details=f"Deleted faculty: {faculty.name} (UID: {faculty.uid})"
#             )

#         faculty.delete()
#         messages.success(request, 'Faculty deleted successfully.')
#         return redirect('departments')  # Redirect after successful deletion

#     context = {
#         'page': page,
#         'page_title': page_title,
#         'profile': profile
#     }

#     return render(request, 'dashboard/delete-confirmation.html', context)
