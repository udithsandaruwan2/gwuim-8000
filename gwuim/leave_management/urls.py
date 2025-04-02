from django.urls import path
from . import views

urlpatterns = [
    path('leave-requests/', views.leaveRequests, name='leave_requests'),
    path('leave-requests-for-approval/', views.leaveRequestsSupervisor, name='leave_requests_for_approval'),
    path('add-leave-request/', views.addLeaveRequestByEmployee, name='add_leave_request_employee'),
]