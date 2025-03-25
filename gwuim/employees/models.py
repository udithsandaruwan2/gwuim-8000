from django.db import models
from departments.models import Department
from users.models import Profile
from decimal import Decimal
from django.db import transaction

class Employee(models.Model):
    #Choices
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    employee_code = models.IntegerField(blank=True, null=True)  
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)
    leave_balance = models.FloatField(default=0.0, blank=True, null=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.employee_code})"

class LeaveType(models.Model):
    code = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    max_days = models.FloatField(default=0.0, blank=True, null=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    
class LeaveRequest(models.Model):
    # Choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    REQUEST_TYPE_CHOICES = [
        ('half', 'Half Day'),
        ('full', 'Full Day'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField(null=False, blank=False)
    coming_date = models.DateField(null=False, blank=False)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES, default='full')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(null=True, blank=True)
    systemized_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    total_days = models.FloatField(default=0.0, editable=False, blank=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.status} for {self.total_days} days)"

    def calculate_total_days(self):
        """Calculate the total number of leave days."""
        if self.start_date and self.coming_date:
            days = (self.coming_date - self.start_date).days
            if days == 0:  # If start and coming dates are the same, add 1
                days = 1
            if self.request_type == 'half':
                return Decimal(days - 0.5)
            return Decimal(days)
        return Decimal(0)

    def save(self, *args, **kwargs):
        """Override save method to handle leave balance."""
        if not self.pk:  # New request
            self.total_days = self.calculate_total_days()  # Correct calculation logic
            # if self.status == 'approved':
            #     with transaction.atomic():
            #         self.employee.leave_balance += self.total_days
            #         self.employee.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Restore leave balance if an approved request is deleted."""
        # if self.status == 'approved':
        #     with transaction.atomic():
        #         self.employee.leave_balance -= self.total_days
        #         self.employee.save()
        super().delete(*args, **kwargs)

class LeaveAdjustment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE)
    adjustment_amount = models.IntegerField()
    reason = models.TextField()
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Adjustment for {self.employee.full_name}"

class MonthlyLeaveSummary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    total_days = models.FloatField(default=0.0, null=True, blank=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('employee', 'year', 'month')

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}-{self.month} : {self.total_days} days"
