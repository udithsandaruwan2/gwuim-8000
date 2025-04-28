from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile
from employees.models import Employee

@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(
            user=instance, 
            username=instance.username, 
            email=instance.email,
            full_name=instance.first_name, 
        )

@receiver(post_save, sender=Profile)
def updateUser(sender, instance, created, **kwargs):
    if instance.user:  # Only update if a user is linked
        instance.user.first_name = instance.full_name
        instance.user.username = instance.username
        instance.user.email = instance.email
        instance.user.save()

@receiver(post_delete, sender=Profile)
def deleteUser(sender, instance, **kwargs):
    user = instance.user
    user.delete()

@receiver(post_save, sender=Profile)
def update_employee_from_profile(sender, instance, created, **kwargs):
    if not created and instance.employee:
        if getattr(instance, '_disable_signal', False):
            return  # skip if signal is disabled
        
        # Normal save
        instance.employee.full_name = instance.full_name
        instance.employee.email = instance.email
        instance.employee.employee_code = instance.username
        
        # Disable Employee signal temporarily
        instance.employee._disable_signal = True
        instance.employee.save()
        del instance.employee._disable_signal

@receiver(post_delete, sender=Profile)
def delete_employee_with_profile(sender, instance, **kwargs):
    if instance.employee:
        instance.employee.delete()
