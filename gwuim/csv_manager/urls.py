from django.urls import path
from . import views

urlpatterns = [
    path('import-export-manager', views.importExport, name='csv_manager'),
]