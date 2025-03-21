import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Faculty, Department
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .utils import search_faculties_departments

@login_required(login_url='login')
def departments(request):
    page = 'departments'
    page_title = 'Departments'
    
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
            return redirect('departments')  # Redirect to refresh the page

        # Handling 'addDepartment' action
        elif request.POST.get('action') == 'addDepartment':
            department_code = request.POST.get('departmentCode')
            department_name = request.POST.get('departmentName')
            faculty_id = request.POST.get('facultyId')

            try:
                faculty = Faculty.objects.get(uid=faculty_id)
                Department.objects.create(code=department_code, name=department_name, faculty=faculty)
            except Faculty.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Faculty not found.'})
            return redirect('departments')  # Redirect to refresh the page
        
        # Handling 'updateDepartments' action for AJAX request
        elif request.POST.get('action') == 'updateDepartments':
            updated_departments = json.loads(request.POST.get('updatedDepartments'))  # Get the list of updated departments
            
            try:
                for dept_data in updated_departments:
                    department = Department.objects.get(uid=dept_data['uid'])
                    department.name = dept_data['name']
                    department.save()

                # Return success response after updating departments
                return JsonResponse({'success': True})
            except Department.DoesNotExist:
                # Return failure response if the department is not found
                return JsonResponse({'success': False, 'error': 'Department not found'})

    context = {
        'page': page,
        'page_title': page_title,
        'faculties': faculties,
        'faculty_departments': faculty_departments,  # Pass the mapping to the template
        'search_query': search_query,
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
                    department.name = dept_data['name']
                    department.save()

                return JsonResponse({'success': True})
            except Faculty.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Faculty not found.'})
            except Department.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Department not found.'})
        return JsonResponse({'success': False, 'message': 'Invalid action.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def deleteDepartmentConfirmation(request, pk):
    page = 'delete_department_type'
    page_title = 'Delete Department Type'

    department = get_object_or_404(Department, uid=pk)  # Ensures object exists

    if request.method == 'POST':
        department.delete()
        return redirect('departments')  # Redirect after successful deletion

    context = {
        'page': page,
        'page_title': page_title,
    }

    return render(request, 'dashboard/delete-confirmation.html', context)

def deleteFacultyConfirmation(request, pk):
    page = 'delete_faculty'
    page_title = 'Delete Faculty'

    faculty = get_object_or_404(Faculty, uid=pk)  # Ensures object exists

    if request.method == 'POST':
        faculty.delete()
        return redirect('departments')  # Redirect after successful deletion

    context = {
        'page': page,
        'page_title': page_title,
    }

    return render(request, 'dashboard/delete-confirmation.html', context)