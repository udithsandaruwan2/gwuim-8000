from django.db import models
from django.contrib.auth import get_user_model
from users.models import Profile

class AuditLog(models.Model):
    action_performed = models.CharField(max_length=255)
    performed_by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    details = models.TextField()
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.action_performed} by {self.performed_by} on {self.created_at}"
