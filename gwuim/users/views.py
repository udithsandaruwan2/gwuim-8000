from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from employees.models import LeaveRequest


def home(request):
    page = 'home'
    page_title = 'Home'

    context = {
        'page': page,
        'page_title': page_title
    }
    return render(request, 'users/index.html', context)

def login(request):
    page = 'login'
    page_title = 'Login'

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
        'page_title': page_title
    }
    return render(request, 'users/login-register.html', context)

@login_required(login_url='login')
def dashboard(request):
    page = 'dashboard'
    page_title = 'Dashboard'

    leave_requests = LeaveRequest.objects.all().order_by('-created_at')[:10]

    context = {
        'page': page,
        'page_title': page_title
    }
    return render(request, 'users/dashboard.html', context)

@login_required(login_url='login')
def logoutView(request):
    user = request.user
    logout(request)
    return redirect('home')
