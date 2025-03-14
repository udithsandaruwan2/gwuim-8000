from django.db import models
from departments.models import Department
class Employee(models.Model):
    #Choices
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    employee_code = models.IntegerField(blank=True, null=True)  
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    leave_balance = models.JSONField(default=dict)
    position = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.employee_code})"
