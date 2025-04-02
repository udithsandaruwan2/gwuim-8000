from django.db import models
from users.models import Profile
import uuid

class AuditLog(models.Model):
    action_performed = models.CharField(max_length=255)
    performed_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    details = models.TextField()
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['performed_by']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action_performed} by {self.performed_by.user.username} at {self.created_at}"