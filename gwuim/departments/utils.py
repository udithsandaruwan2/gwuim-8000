from .models import Department, Faculty
from django.db.models import Q

def search_faculties_departments(request):
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

    return faculties, departments, search_query
