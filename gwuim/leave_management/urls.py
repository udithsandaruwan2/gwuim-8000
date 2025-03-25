from django.urls import path
from . import views

urlpatterns = [
    path('leave-requests/', views.leaveRequets, name='leave_requests')

]