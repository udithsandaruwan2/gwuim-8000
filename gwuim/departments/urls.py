from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.departments, name='departments'),

    path('departments/delete-confirmation/', views.deleteConfirmation, name='delete_confirmation'),
    path('departments/', views.update_departments, name='update_departments'),
]