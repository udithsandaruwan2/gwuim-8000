from django.urls import path
from . import views

urlpatterns = [
    path('employees', views.employees, name='employees'),
    path('employee/<str:pk>', views.employeeIndetail, name='employee-indetail'),
    path('download-report/<str:pk>/', views.downloadReport, name='download_report'),

    # Leave 
    path('leave-types/', views.leaveTypes, name='leave_types'),
    path('leave-types/<str:pk>/update', views.updateLeaveType, name='update_leave_type'),
    path('leave-types/<str:pk>/delete', views.deleteLeaveTypeConfirmation, name='delete_leave_type'),
    path('leave-requests-history/<str:pk>', views.employeeLeaveHistory, name='leave_requests_history'),
]