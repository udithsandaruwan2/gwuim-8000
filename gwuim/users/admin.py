from django.contrib import admin
from .models import UserRole, Profile, TemporaryUserPass

admin.site.register(UserRole)
admin.site.register(Profile)
admin.site.register(TemporaryUserPass)
