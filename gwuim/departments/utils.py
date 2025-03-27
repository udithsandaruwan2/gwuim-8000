from .models import Department, Faculty
from django.db.models import Q
from audit_logs.utils import create_audit_log

def search_faculties_departments(request):
    # Retrieve the search query from GET parameters
    search_query = request.GET.get('search', '').strip()

    # Search Faculty
    faculties = Faculty.objects.filter(
        Q(code__icontains=search_query) |
        Q(name__icontains=search_query)
    )

    # Search Department (with related Faculty)
    departments = Department.objects.select_related('faculty').filter(
        Q(code__icontains=search_query) |
        Q(name__icontains=search_query) |
        Q(faculty__name__icontains=search_query)  # Optimized faculty search
    )

    # Log the search action in the audit log
    if request.user.is_authenticated:
        create_audit_log(
            action_performed="Searched Faculties and Departments",
            performed_by=request.user.profile,  # Assuming the user has a Profile object
            details=f"Searched with query: '{search_query}'"
        )

    # Return the results: Faculties, Departments, and the search query
    return faculties, departments, search_query
