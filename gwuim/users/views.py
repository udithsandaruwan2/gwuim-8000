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


def home(request):
    page = 'home'
    page_title = 'Home'

    try:
        profile = request.user.profile
    except:
        profile = None

    context = {
        'page': page,
        'page_title': page_title,
        'profile':profile
    }
    return render(request, 'users/index.html', context)

def login(request):
    page = 'login'
    page_title = 'Login'

    try:
        profile = request.user.profile
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
        return redirect('dashboard')


    context = {
        'page': page,
        'page_title': page_title,
        'profile':profile
    }
    return render(request, 'users/login-register.html', context)

@login_required(login_url='login')
def dashboard(request):
    page = 'dashboard'
    page_title = 'Dashboard'

    try:
        profile = request.user.profile
    except:
        profile = None

    leave_requests = LeaveRequest.objects.all().order_by('-created_at')[:5]
    leave_requests_count = LeaveRequest.objects.all().count()

    context = {
        'page': page,
        'page_title': page_title,
        'leave_requests': leave_requests,
        'leave_requests_count': leave_requests_count,
        'profile':profile
    }
    return render(request, 'users/dashboard.html', context)

@login_required(login_url='login')
def logoutView(request):
    user = request.user
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def leave_requests_chart_data(request):
    year = int(request.GET.get('year', datetime.now().year))  # Default to current year

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
    data = {
        'labels': ['Approved', 'Rejected', 'Pending'],
        'values': [
            LeaveRequest.objects.filter(status='approved').count(),
            LeaveRequest.objects.filter(status='rejected').count(),
            LeaveRequest.objects.filter(status='pending').count(),
        ]
    }
    return JsonResponse(data)
