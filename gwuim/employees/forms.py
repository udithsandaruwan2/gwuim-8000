from django import forms
from .models import Employee, LeaveRequest, LeaveType


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_code',
            'full_name', #
            'email', #
            'gender', #
            'position', 
            'department', 
            'date_of_joining',
            'date_of_leaving',
            'date_of_birth',#
            'nic',
            'address'
        ]
        widgets = {
            'employee_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'employeeCode'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'employeeName'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'employeeEmail'}),
            'gender': forms.Select(choices=Employee.GENDER_CHOICES, attrs={'class': 'form-control', 'id': 'employeeGender'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'id': 'employeePosition'}),
            'department': forms.Select(attrs={'class': 'form-control', 'id': 'employeeDepartment'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'id': 'employeeStartDate', 'type': 'date'}),
            'date_of_leaving': forms.DateInput(attrs={'class': 'form-control', 'id': 'employeeEndDate', 'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'id': 'employeeBirthDate', 'type': 'date'}),
            'nic': forms.TextInput(attrs={'class': 'form-control', 'id': 'employeeEmail'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'id': 'employeeAddress', 'rows': 3}),
        }
        contact_number = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                'class': 'form-control custom-input',
                'placeholder': 'Eg: +123456789'
            })
        )

        error_messages = {
            'employee_code': {
            'required': 'Employee code is required.',
            },
        }


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['code', 'name', 'max_days', 'description']  # Include code, name, and description fields

    # Add custom widget with the desired styling for each field
    code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2 edit-input',  # Add the classes here
            'placeholder': 'Enter leave type code',  # Optionally add a placeholder
        }),
        required=False  # Set this to False if code is optional
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2 edit-input',  # Add the classes here
            'placeholder': 'Enter leave type name',  # Optionally add a placeholder
        })
    )

    max_days = forms.FloatField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2 edit-input',  # Add the classes here
            'placeholder': 'Enter maximum allocating days',  # Optionally add a placeholder
        })
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control mt-2 edit-input',  # Add the classes here
            'placeholder': 'Enter leave type description',  # Optionally add a placeholder
            'rows': 3,  # You can adjust the rows for the textarea
        }),
        required=False  # Set this to False if description is optional
    )
