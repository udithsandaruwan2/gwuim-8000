from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils import searchRequests, paginateRequests, searchRequestsSupervisor
from django.utils import timezone
from audit_logs.utils import create_audit_log
from employees.models import LeaveRequest, LeaveType, Employee
from departments.models import Department
from employees.utils import calculate_total_days
from django.contrib import messages
from users.models import Profile

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
            
            messages.success(request, f'Leave request {request_id} status updated to {status}.')
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


def addLeaveRequestByEmployee(request):
    """View to handle adding a new leave request."""
    page = 'add_leave_request_employee'
    page_title = 'Add Leave Request (Employee)'
     # Get all leave types for selection
    leave_types = LeaveType.objects.all()
    # Log the action: User accessed the add leave request page

    if request.method == 'POST':
        employee = Employee.objects.get(employee_code=request.POST.get('code'))  # Get the employee object
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
            status = 'pending'
            # Create leave request and log it
            leave_request = LeaveRequest.objects.create(
                employee=employee,
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
                performed_by=Profile.objects.get(employee=employee),
                details=f"Leave request added for employee {employee.full_name} ({employee.employee_code})"
            )
        else:
            messages.error(request, f'Insufficient leave balance in {leave_type}.')
        
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('home')


    context = {
        'page': page,
        'page_title': page_title,
        'leave_types': leave_types,  # Include all leave types for selection
    }

    return render(request, 'leave_management/add-leave-request.html', context)

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