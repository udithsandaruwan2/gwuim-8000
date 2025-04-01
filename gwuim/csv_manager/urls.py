from django.urls import path
from . import views

urlpatterns = [
    path('import-export-manager', views.importExport, name='csv_manager'),
    path('export-employees/', views.export_employees_csv, name='export_employees_csv'),
]