from django.urls import path
from . import views

urlpatterns = [
    path('employees', views.employees, name='employees'),
    path('employee/<str:pk>', views.employeeIndetail, name='employee-indetail'),
    path('download-report/<str:pk>/', views.downloadReport, name='download_report'),
]