import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Faculty, Department
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import search_faculties_departments
from audit_logs.utils import create_audit_log

@login_required(login_url='login')
def departments(request):
    page = 'departments'
    page_title = 'Departments'

    try:
        profile = request.user.profile
    except:
        profile = None

    # Log the view page action
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Viewed Departments Page",
            performed_by=request.user.profile,  # Assuming the user has a Profile object
            details="User viewed the departments page."
        )

    faculties, departments, search_query = search_faculties_departments(request)

    # Create a dictionary to map faculty to their departments
    faculty_departments = {faculty.uid: [] for faculty in faculties}
    for department in departments:
        if department.faculty:  # Check if the faculty is not None
            faculty_departments[department.faculty.uid].append(department)

    # Handle POST request for adding faculty or department
    if request.method == 'POST':
        # Handling 'addFaculty' action
        if request.POST.get('action') == 'addFaculty':
            faculty_code = request.POST.get('facultyCode')
            faculty_name = request.POST.get('facultyName')
            Faculty.objects.create(code=faculty_code, name=faculty_name)

            # Log the action of adding a faculty
            if request.user.is_authenticated:
                create_audit_log(
                    action_performed="Added Faculty",
                    performed_by=request.user.profile,
                    details=f"Added faculty with code: {faculty_code}, name: {faculty_name}"
                )
            
            messages.success(request, 'Faculty added successfully.')
            return redirect('departments')  # Redirect to refresh the page

        # Handling 'addDepartment' action
        elif request.POST.get('action') == 'addDepartment':
            department_code = request.POST.get('departmentCode')
            department_name = request.POST.get('departmentName')
            faculty_id = request.POST.get('facultyId')

            try:
                faculty = Faculty.objects.get(uid=faculty_id)
                Department.objects.create(code=department_code, name=department_name, faculty=faculty)

                # Log the action of adding a department
                if request.user.is_authenticated:
                    create_audit_log(
                        action_performed="Added Department",
                        performed_by=request.user.profile,
                        details=f"Added department with code: {department_code}, name: {department_name}, under faculty: {faculty.name}"
                    )
            except Faculty.DoesNotExist:
                messages.error(request, 'Faculty not found.')
                return JsonResponse({'success': False, 'error': 'Faculty not found.'})
            
            messages.success(request, 'Department added successfully.')
            return redirect('departments')  # Redirect to refresh the page

        # Handling 'updateDepartments' action for AJAX request
        elif request.POST.get('action') == 'updateDepartments':
            updated_departments = json.loads(request.POST.get('updatedDepartments'))  # Get the list of updated departments
            
            try:
                for dept_data in updated_departments:
                    department = Department.objects.get(uid=dept_data['uid'])
                    old_name = department.name
                    department.name = dept_data['name']
                    department.save()

                    # Log the action of updating a department
                    if request.user.is_authenticated:
                        create_audit_log(
                            action_performed="Updated Department",
                            performed_by=request.user.profile,
                            details=f"Updated department from name: {old_name} to {department.name}"
                        )
                messages.success(request, 'Departments updated successfully.')
                # Return success response after updating departments
                return JsonResponse({'success': True})
            except Department.DoesNotExist:
                messages.error(request, 'Department not found.')
                # Return failure response if the department is not found
                return JsonResponse({'success': False, 'error': 'Department not found'})

    context = {
        'page': page,
        'page_title': page_title,
        'faculties': faculties,
        'faculty_departments': faculty_departments,  # Pass the mapping to the template
        'search_query': search_query,
        'profile': profile
    }
    return render(request, 'departments/departments.html', context)

@login_required(login_url='login')
@csrf_exempt  # Use this only if necessary
def update_departments(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'updateDepartments':
            faculty_uid = data.get('facultyUid')
            updated_departments = data.get('updatedDepartments')

            try:
                faculty = Faculty.objects.get(uid=faculty_uid)

                # Update department names
                for dept_data in updated_departments:
                    department = Department.objects.get(uid=dept_data['uid'], faculty=faculty)
                    old_name = department.name
                    department.name = dept_data['name']
                    department.save()

                    # Log the department update action
                    if request.user.is_authenticated:
                        create_audit_log(
                            action_performed="Updated Department",
                            performed_by=request.user.profile,
                            details=f"Updated department from name: {old_name} to {department.name}, under faculty: {faculty.name}"
                        )
                messages.success(request, 'Departments updated successfully.')
                return JsonResponse({'success': True})
            except Faculty.DoesNotExist:
                messages.error(request, 'Faculty not found.')
                return JsonResponse({'success': False, 'error': 'Faculty not found.'})
            except Department.DoesNotExist:
                messages.error(request, 'Department not found.')
                return JsonResponse({'success': False, 'error': 'Department not found.'})
        messages.error(request, 'Invalid action.')
        return JsonResponse({'success': False, 'message': 'Invalid action.'})
    messages.error(request, 'Invalid request method.')
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required(login_url='login')
def deleteDepartmentConfirmation(request, pk):
    page = 'delete_department_type'
    page_title = 'Delete Department Type'

    try:
        profile = request.user.profile
    except:
        profile = None

    department = get_object_or_404(Department, uid=pk)  # Ensures object exists

    # Log the deletion action (before actually deleting the department)
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Viewed Department Deletion Confirmation",
            performed_by=request.user.profile,
            details=f"User is about to delete department: {department.name} (UID: {department.uid})"
        )

    if request.method == 'POST':
        # Log the department deletion
        if request.user.is_authenticated:
            create_audit_log(
                action_performed="Deleted Department",
                performed_by=request.user.profile,
                details=f"Deleted department: {department.name} (UID: {department.uid})"
            )

        department.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('departments')  # Redirect after successful deletion

    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile
    }

    return render(request, 'dashboard/delete-confirmation.html', context)

@login_required(login_url='login')
def deleteFacultyConfirmation(request, pk):
    page = 'delete_faculty'
    page_title = 'Delete Faculty'

    try:
        profile = request.user.profile
    except:
        profile = None

    faculty = get_object_or_404(Faculty, uid=pk)  # Ensures object exists

    # Log the deletion action (before actually deleting the faculty)
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Viewed Faculty Deletion Confirmation",
            performed_by=request.user.profile,
            details=f"User is about to delete faculty: {faculty.name} (UID: {faculty.uid})"
        )

    if request.method == 'POST':
        # Log the faculty deletion
        if request.user.is_authenticated:
            create_audit_log(
                action_performed="Deleted Faculty",
                performed_by=request.user.profile,
                details=f"Deleted faculty: {faculty.name} (UID: {faculty.uid})"
            )

        faculty.delete()
        messages.success(request, 'Faculty deleted successfully.')
        return redirect('departments')  # Redirect after successful deletion

    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile
    }

    return render(request, 'dashboard/delete-confirmation.html', context)
