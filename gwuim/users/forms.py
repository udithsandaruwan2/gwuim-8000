from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password1', 'password2']
        labels = {
            'first_name':'name', 
        }   
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update(
            {'type':'text', 'class':"form-control", 'placeholder':'Full Name'}
        )
        
        self.fields['username'].widget.attrs.update(
            {'type':'text', 'class':"form-control", 'placeholder':'Username'}
        )

        self.fields['email'].widget.attrs.update(
            {'type':'email', 'class':"form-control", 'placeholder':'Email'}
        )

        self.fields['password1'].widget.attrs.update(
            {'type':'password', 'class':"form-control", 'placeholder':'Password'}
        )

        self.fields['password2'].widget.attrs.update(
            {'type':'password', 'class':"form-control", 'placeholder':'Confirm Password'}
        )


