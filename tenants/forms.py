from django import forms
from tenants.models import Tenant

class TenantCreationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'subdomain']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your clinic/organization name',
                'required': True,
            }),
            'subdomain': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'your-clinic (must be unique)',
                'required': True,
                'pattern': '[a-z0-9-]+',
                'help_text': 'Lowercase letters, numbers, and hyphens only',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = 'The official name of your healthcare organization'
        self.fields['subdomain'].help_text = 'Used in your unique clinic URL (e.g., your-clinic.cliniccloud.com)'

