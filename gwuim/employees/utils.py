from .models import Employee
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def searchEmployees(request):
    search_query = request.GET.get('search', '')

    employees = Employee.objects.distinct().filter(
        Q(employee_code__icontains=search_query) |
        Q(full_name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(position__icontains=search_query) |
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
