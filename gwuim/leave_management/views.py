from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils import searchRequests, paginateRequests, searchRequestsSupervisor
from audit_logs.utils import create_audit_log
from employees.models import LeaveRequest
from departments.models import Department

@login_required(login_url='login')
def leaveRequests(request):
    """View to handle the display of leave requests with pagination and search."""
    page = 'leave_requests'
    page_title = 'Leave Requests'

    profile = getattr(request.user, 'profile', None)  # Get user profile safely

    # Log the action: User accessed the leave requests page
    create_audit_log(
        action_performed="Accessed Leave Requests Page",
        performed_by=profile,
        details="User accessed the leave requests page."
    )

    # Queries with pagination
    requests_queryset, search_query = searchRequests(request)  # Search leave requests
    custom_range, requests_paginated = paginateRequests(request, requests_queryset, 10)  # Paginate results
    departments = Department.objects.all()  # Get all departments

    context = {
        'page': page,
        'page_title': page_title,
        'requests': requests_paginated,  # Pass paginated requests to template
        'search_query': search_query,  # Include search query for filtering
        'custom_range': custom_range,  # Include custom pagination range
        'profile': profile,  # Include user profile for user-specific info
        'departments': departments  # Include all departments for filtering
    }
    
    return render(request, 'leave_management/leave_requests.html', context)

@login_required(login_url='login')
def leaveRequestsSupervisor(request):
    """View to handle the display of leave requests with pagination and search."""
    page = 'leave_requests'
    page_title = 'Leave Requests'

    profile = getattr(request.user, 'profile', None)  # Get user profile safely

    # Log the action: User accessed the leave requests page
    create_audit_log(
        action_performed="Accessed Leave Requests Page",
        performed_by=profile,
        details="User accessed the leave requests page."
    )

    # Queries with pagination
    requests_queryset, search_query = searchRequestsSupervisor(request)  # Search leave requests
    custom_range, requests_paginated = paginateRequests(request, requests_queryset, 10)  # Paginate results
    departments = Department.objects.all()  # Get all departments

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'updateRequest':
            request_id = request.POST.get('requestId')
            status = request.POST.get('status')
            
            leave_request = get_object_or_404(LeaveRequest, uid=request_id)  # Ensure request exists
            leave_request.status = status
            leave_request.save()
            
            create_audit_log(
                action_performed="Updated Leave Request Status",
                performed_by=profile,
                details=f"User updated leave request {request_id} to status {status}."
            )
            
            return redirect('leave_requests_for_approval') 

    context = {
        'page': page,
        'page_title': page_title,
        'requests': requests_paginated,  # Pass paginated requests to template
        'search_query': search_query,  # Include search query for filtering
        'custom_range': custom_range,  # Include custom pagination range
        'profile': profile,  # Include user profile for user-specific info
        'departments': departments,  # Include all departments for filtering
    }
    
    return render(request, 'leave_management/leave_requests.html', context)


# @login_required(login_url='login')
# def deleteLeaveTypeConfirmation(request, pk):
#     page = 'delete_leave_request'
#     page_title = 'Delete Leave Type'

#     try:
#         profile = request.user.profile
#     except:
#         profile = None

#     leave_type = get_object_or_404(LeaveType, uid=pk)  # Ensures object exists

#     if request.method == 'POST':
#         leave_type.delete()
#         # Log action: Delete Leave Type
#         create_audit_log(
#             action_performed="Deleted Leave Type",
#             performed_by=request.user.profile,
#             details=f"Deleted leave type {leave_type.name} (Code: {leave_type.code})"
#         )
#         return redirect('leave_types')  # Redirect after successful deletion

#     context = {
#         'page': page,
#         'page_title': page_title,
#         'leave_type': leave_type,  # Pass object to template for display
#         'profile': profile
#     }

#     return render(request, 'dashboard/delete-confirmation.html', context)