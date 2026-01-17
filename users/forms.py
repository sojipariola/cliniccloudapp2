from django import forms
from django.contrib.auth.forms import AuthenticationForm

from tenants.models import Tenant


class TenantAwareAuthenticationForm(AuthenticationForm):
    tenant = forms.CharField(label="Tenant", max_length=100, required=True)

    def clean(self):
        # Avoid calling AuthenticationForm.clean() to suppress the default
        # "Please enter a correct username and password" non-field error.
        cleaned_data = super(forms.Form, self).clean()

        tenant_identifier = cleaned_data.get("tenant")
        try:
            tenant = Tenant.objects.get(name=tenant_identifier)
        except Tenant.DoesNotExist:
            raise forms.ValidationError("Invalid tenant identifier.")

        self.cleaned_data["tenant_obj"] = tenant
        return self.cleaned_data
