from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from employees.models import LeaveRequest
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import calendar
from datetime import datetime
from audit_logs.utils import create_audit_log
from .models import Profile


def home(request):
    """Home page view."""
    page = 'home'
    page_title = 'Home'

    try:
        profile = request.user.profile  # Get user profile if available
    except:
        profile = None

    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile
    }
    return render(request, 'users/index.html', context)


def login(request):
    """Login view for user authentication."""
    page = 'login'
    page_title = 'Login'

    try:
        profile = request.user.profile  # Get user profile if available
    except:
        profile = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Validate input
        if not username:
            messages.error(request, 'Username is required')
            return redirect('login')

        if not password:
            messages.error(request, 'Password is required')
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Email or password is incorrect')
            return redirect('login')

        auth_login(request, user)

        # Log the action: User logged in successfully
        create_audit_log(
            action_performed="User Logged In",
            performed_by=user.profile,
            details=f"User {username} logged in."
        )

        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('dashboard')

    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile
    }
    return render(request, 'users/login-register.html', context)


@login_required(login_url='login')
def dashboard(request):
    """Dashboard view for logged-in users."""
    page = 'dashboard'
    page_title = 'Dashboard'

    try:
        profile = request.user.profile  # Get user profile if available
    except:
        profile = None

    leave_requests = LeaveRequest.objects.all().order_by('-created_at')[:5]
    leave_requests_count = LeaveRequest.objects.all().count()

    # Log the action: User accessed the dashboard
    create_audit_log(
        action_performed="Accessed Dashboard",
        performed_by=profile,
        details="User accessed the dashboard page."
    )

    context = {
        'page': page,
        'page_title': page_title,
        'leave_requests': leave_requests,
        'leave_requests_count': leave_requests_count,
        'profile': profile
    }
    return render(request, 'users/dashboard.html', context)


@login_required(login_url='login')
def logoutView(request):
    """Logout view to log out the user."""
    user = request.user
    logout(request)

    # Log the action: User logged out
    create_audit_log(
        action_performed="User Logged Out",
        performed_by=user.profile,
        details=f"User {user.username} logged out."
    )

    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def profile(request, pk):
    """Profile view for the logged-in user."""
    page = 'profile'
    page_title = 'Profile'

    try:
        profile = Profile.objects.get(uid=pk)  # Get user profile by UID
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('employees')

    if request.method == 'POST':
        # Handle profile update logic here
        pass

    context = {
        'page': page,
        'page_title': page_title,
        'profile': profile
    }
    return render(request, 'users/profile.html', context)


@login_required(login_url='login')
def leave_requests_chart_data(request):
    """View to fetch and return leave request data for the chart."""
    year = int(request.GET.get('year', datetime.now().year))  # Default to current year

    # Log the action: User accessed leave requests chart data
    create_audit_log(
        action_performed="Accessed Leave Requests Chart Data",
        performed_by=request.user.profile,
        details=f"User accessed leave requests chart data for the year {year}."
    )

    # Generate a dictionary with all months initialized to 0
    monthly_data = {f"{month} {year}": 0 for month in calendar.month_name[1:]}

    # Fetch data from the database
    data = (
        LeaveRequest.objects
        .filter(start_date__year=year)
        .annotate(month=TruncMonth('start_date'))
        .values('month')
        .annotate(total_leaves=Sum('total_days'))
        .order_by('month')
    )

    # Update monthly_data with real values
    for entry in data:
        month_str = entry['month'].strftime('%B %Y')
        monthly_data[month_str] = entry['total_leaves']

    # Format data for chart
    chart_data = {
        'labels': list(monthly_data.keys()),
        'values': list(monthly_data.values()),
    }

    return JsonResponse(chart_data)


@login_required(login_url='login')
def leave_requests_pie_chart_data(request):
    """View to fetch and return leave request pie chart data."""
    # Log the action: User accessed leave requests pie chart data
    create_audit_log(
        action_performed="Accessed Leave Requests Pie Chart Data",
        performed_by=request.user.profile,
        details="User accessed leave requests pie chart data."
    )

    data = {
        'labels': ['Approved', 'Rejected', 'Pending'],
        'values': [
            LeaveRequest.objects.filter(status='approved').count(),
            LeaveRequest.objects.filter(status='rejected').count(),
            LeaveRequest.objects.filter(status='pending').count(),
        ]
    }
    return JsonResponse(data)

