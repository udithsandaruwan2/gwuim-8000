from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import EmployeeSerializer, TitleSerializer
from employees.models import Employee, Title


@api_view(['GET'])
def getRoutes(request):
    """View to display available API routes."""
    routes = [
        'api/employees/',
        'api/employees/<str:pk>/',
        'api/titles/',
        
    ]
    return Response(routes)

@api_view(['GET'])
def getEmployeeList(request):
    """View to retrieve a list of employees."""
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEmployeeDetail(request, pk):
    """View to retrieve details of a specific employee."""
    employee = Employee.objects.get(uid=pk)
    serializer = EmployeeSerializer(employee, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getTitleList(request):
    """View to retrieve a list of titles."""
    titles = Title.objects.all()
    serializer = TitleSerializer(titles, many=True)
    return Response(serializer.data)