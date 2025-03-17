from django.shortcuts import render

def departments(request):
    page = 'departments'
    page_title = 'Departments'

    context = {
        'page': page,
        'page_title': page_title,
    }
    return render(request, 'departments/departments.html', context)

def updateDepartment(request, faculty_name):
    page = 'update_department'
    page_title = 'Update Department'

    context = {
        'page': page,
        'page_title': page_title,
        'faculty_name': faculty_name,
    }
    return render(request, 'departments/departments.html', context)
