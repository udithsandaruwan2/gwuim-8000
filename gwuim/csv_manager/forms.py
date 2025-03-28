# forms.py
from django import forms
from .models import EmployeeFile

class EmployeeFileForm(forms.ModelForm):
    class Meta:
        model = EmployeeFile
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control mt-2 edit-input',
            }),
        }
