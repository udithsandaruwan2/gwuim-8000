from django import forms
from .models import Employee, LeaveRequest, LeaveType

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_code', 'full_name', 'email', 'gender', 'position', 'department', 'date_of_joining']
        widgets = {
            'employee_code': forms.NumberInput(attrs={'class': 'form-control', 'id': 'employeeCode'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'employeeName'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'employeeEmail'}),
            'gender': forms.Select(choices=Employee.GENDER_CHOICES, attrs={'class': 'form-control', 'id': 'employeeGender'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'id': 'employeePosition'}),
            'department': forms.Select(attrs={'class': 'form-control', 'id': 'employeeDepartment'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'id': 'employeeStartDate', 'type': 'date'}),
        }
