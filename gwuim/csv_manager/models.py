from django.db import models
import uuid

class EmployeeFile(models.Model):
    file = models.FileField(upload_to='employee_files/', null=False, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Common fields
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"File uploaded at {self.uploaded_at}"
