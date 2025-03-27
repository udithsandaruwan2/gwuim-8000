from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import searchRequests, paginateRequests
from .utils import create_audit_log  # Assuming create_audit_log function is defined in utils.py

@login_required(login_url='login')
def leaveRequets(request):
    """View to handle the display of leave requests with pagination and search."""
    page = 'leave_requests'
    page_title = 'Leave Requests'

    try:
        profile = request.user.profile  # Get the user profile
    except:
        profile = None

    # Log the action: User accessed the leave requests page
    create_audit_log(
        action_performed="Accessed Leave Requests Page",
        performed_by=profile,  # Assuming the user has a profile
        details="User accessed the leave requests page."
    )

    # Queries with pagination
    requests, search_query = searchRequests(request)  # Search leave requests
    custom_range, requests = paginateRequests(request, requests, 10)  # Paginate results

    context = {
        'page': page,
        'page_title': page_title,
        'requests': requests,  # Pass requests to template
        'search_query': search_query,  # Include search query for filtering
        'custom_range': custom_range,  # Include custom pagination range
        'profile': profile  # Include user profile for user-specific info
    }
    
    return render(request, 'leave_management/leave_requests.html', context)
