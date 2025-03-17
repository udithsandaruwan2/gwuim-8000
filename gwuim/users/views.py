from django.shortcuts import render

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

    context = {
        'page': page,
        'page_title': page_title
    }
    return render(request, 'users/login-register.html', context)

def dashboard(request):
    page = 'dashboard'
    page_title = 'Dashboard'

    context = {
        'page': page,
        'page_title': page_title
    }
    return render(request, 'users/dashboard.html', context)


