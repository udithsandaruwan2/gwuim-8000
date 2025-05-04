from django.urls import path
from . import views

urlpatterns = [

    path('', views.getRoutes, name='routes'),
    path('employees/', views.getEmployeeList, name='employee_list'),
    path('employees/<str:pk>/', views.getEmployeeDetail, name='employee_detail')
]
