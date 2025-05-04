from rest_framework import serializers
from django.contrib.auth.models import User
from employees.models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    class Meta:
        model = Employee
        fields = '__all__'  # Include all fields from the Employee model