from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.departments, name='departments'),
    path('departments/<str:faculty_name>/', views.updateDepartment, name='update_department'),
]