from django.db import models


class Department(models.Model):
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    
    # Operations
    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super(Department, self).save(*args, **kwargs)


# from .employees import Employee
"""
Department Addition Attributes
- head = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True)
"""
