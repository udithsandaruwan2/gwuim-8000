from django.db import models
from django.contrib.auth.models import User

class UserRole(models.Model):
    role_name = models.CharField(max_length=20, unique=True, blank=False)
    description = models.TextField(blank=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uid} - {self.role_name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=50)
    username = models.CharField(max_length=20, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    email = models.EmailField()
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, null=True, blank=True)
    # Common fields
    uid = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name}"


