from django.urls import path
from . import views

urlpatterns = [
    path('employees', views.employees, name='employees'),
    path('employee/<str:pk>', views.employeeIndetail, name='employee-indetail'),
    path('employee/att/<str:pk>/', views.employeeIndetailFromAttendance, name='employee_indetail_from_att'),
    path('download-report/<str:pk>/', views.downloadReport, name='download_report'),
    path('leave-types/', views.leaveTypes, name='leave_types'),
    path('leave-types/<str:pk>/update', views.updateLeaveType, name='update_leave_type'),
    path('leave-types/<str:pk>/delete', views.deleteLeaveTypeConfirmation, name='delete_leave_type'),
    path('leave-requests-history/<str:pk>', views.employeeLeaveHistory, name='leave_requests_history'),
    path('employee/<str:pk>/view', views.employee, name='view_employee'),

    path('get-other-leave-data/<int:_id>/<int:_year>/<int:_month>/', views.get_other_leave_data, name='get_other_leave_data'),
]