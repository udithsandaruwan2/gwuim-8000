from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from employees.models import LeaveRequest
from datetime import datetime

# def searchRequests(request):
#     search_query = request.GET.get('search', '')
#     # Use the double underscore syntax to filter by the 'name' field of the related models
#     requests = LeaveRequest.objects.distinct().filter(
#         Q(employee__employee_code__icontains=search_query) |
#         Q(employee__full_name__icontains=search_query) |  # Corrected lookup for employee's name
#         Q(leave_type__name__icontains=search_query) |  # Corrected lookup for leave type's name
#         Q(employee__department__name__icontains=search_query) |  # Corrected lookup for department's name
#         Q(request_type__icontains=search_query)
#     )
    
#     return requests, search_query

def searchRequestsSupervisor(request):
    search_query = request.GET.get('search', '')
    # Use the double underscore syntax to filter by the 'name' field of the related models
    requests = LeaveRequest.objects.distinct().filter(
        Q(employee__employee_code__icontains=search_query) |  # Corrected lookup for employee's code
        Q(employee__full_name__icontains=search_query) |  # Corrected lookup for employee's name
        Q(leave_type__name__icontains=search_query) |  # Corrected lookup for leave type's name
        Q(request_type__icontains=search_query),  # Correct lookup for request_type
        status='pending',  # Filter only pending requests
        employee__department=request.user.profile.department  # Filter by the user's department
        
    )
    
    
    return requests, search_query



def searchRequests(request):
    search_query = request.GET.get('search', '').strip()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    requests = LeaveRequest.objects.all()

    # Filter by employee_id if numeric
    if search_query.isdigit():
        requests = requests.filter(employee_code=search_query)
    elif search_query:
        requests = LeaveRequest.objects.distinct().filter(
            Q(employee__full_name__icontains=search_query) |
            Q(leave_type__name__icontains=search_query) |
            Q(employee__department__name__icontains=search_query) |
            Q(request_type__icontains=search_query)
        )
    else:
        requests = LeaveRequest.objects.all()

    # Filter by date range if both dates are provided
    try:
        if from_date and to_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            requests = requests.filter(
                Q(start_date__range=(from_date, to_date)) |
                Q(coming_date__range=(from_date, to_date))
            )
        elif from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            requests = requests.filter(Q(start_date__gte=from_date) | Q(coming_date__gte=from_date))
        elif to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            requests = requests.filter(Q(start_date__lte=to_date) | Q(coming_date__lte=to_date))
    except ValueError:
        requests = LeaveRequest.objects.none()

    return requests, search_query, from_date, to_date



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
