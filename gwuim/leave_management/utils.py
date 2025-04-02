from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from employees.models import LeaveRequest

def searchRequests(request):
    search_query = request.GET.get('search', '')
    # Use the double underscore syntax to filter by the 'name' field of the related models
    requests = LeaveRequest.objects.distinct().filter(
        Q(employee__employee_code__icontains=search_query) |
        Q(employee__full_name__icontains=search_query) |  # Corrected lookup for employee's name
        Q(leave_type__name__icontains=search_query) |  # Corrected lookup for leave type's name
        Q(employee__department__name__icontains=search_query) |  # Corrected lookup for department's name
        Q(request_type__icontains=search_query)
    )
    
    return requests, search_query

def searchRequestsSupervisor(request):
    search_query = request.GET.get('search', '')
    # Use the double underscore syntax to filter by the 'name' field of the related models
    requests = LeaveRequest.objects.distinct().filter(
        Q(employee__employee_code__icontains=search_query) |  # Corrected lookup for employee's code
        Q(employee__full_name__icontains=search_query) |  # Corrected lookup for employee's name
        Q(leave_type__name__icontains=search_query) |  # Corrected lookup for leave type's name
        Q(employee__department__name__icontains=search_query) |  # Corrected lookup for department's name
        Q(request_type__icontains=search_query),  # Correct lookup for request_type
        status='pending',  # Filter only pending requests
        
    )
    
    return requests, search_query

def paginateRequests(request, requests, results):
    page = request.GET.get('page', 1)  # Default to page 1 if not provided
    paginator = Paginator(requests, results)

    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        requests = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        requests = paginator.page(page)

    try:
        page = int(page)
    except ValueError:
        page = 1  # Default to page 1 if conversion fails

    left_index = max(page - 1, 1)
    right_index = min(page + 2, paginator.num_pages + 1)

    custom_range = range(left_index, right_index)
    return custom_range, requests
