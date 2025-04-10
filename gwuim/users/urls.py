from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/leave-requests-chart-data/', views.leave_requests_chart_data, name='leave_requests_chart_data'),
    path('api/leave-requests-pie-chart-data/', views.leave_requests_pie_chart_data, name='leave_requests_pie_chart_data'),
    path('profile/', views.profile, name='profile'),
]