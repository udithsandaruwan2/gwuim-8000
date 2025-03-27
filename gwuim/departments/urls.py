from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.departments, name='departments'),
    path('departments/', views.update_departments, name='update_departments'),
    path('departments/<str:pk>/delete', views.deleteDepartmentConfirmation, name='delete_department'),
    path('faculties/<str:pk>/delete', views.deleteFacultyConfirmation, name='delete_faculty'),
]