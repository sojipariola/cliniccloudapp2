from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from tenants.models import Tenant
from users.models import CustomUser


class TenantUserRegistrationForm(UserCreationForm):
    # Choice: Join existing company or create new one
    registration_type = forms.ChoiceField(
        choices=[("join", "Join Existing Company"), ("create", "Create New Company")],
        widget=forms.RadioSelect,
        initial="create",
        label="Registration Type",
    )

    # For joining existing company
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.filter(is_active=True),
        label="Select Company",
        required=False,
        help_text="Select your company if you're joining an existing organization",
    )

    # For creating new company
    company_name = forms.CharField(
        max_length=100,
        required=False,
        label="Company Name",
        help_text="Name of your clinic, hospital, or healthcare organization",
    )

    specialization = forms.ChoiceField(
        choices=Tenant.SPECIALIZATION_CHOICES,
        required=False,
        initial="general_practice",
        label="Specialization",
        help_text="Primary medical specialty of your organization",
    )

    email = forms.EmailField(required=True)
    role = forms.CharField(label="Role", max_length=50, required=False, initial="user")

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "registration_type",
            "tenant",
            "company_name",
            "specialization",
            "role",
            "password1",
            "password2",
        )

    def clean(self):
        cleaned_data = super().clean()
        registration_type = cleaned_data.get("registration_type")
        tenant = cleaned_data.get("tenant")
        company_name = cleaned_data.get("company_name")

        # Validate based on registration type
        if registration_type == "join":
            if not tenant:
                raise forms.ValidationError("Please select a company to join.")
        elif registration_type == "create":
            if not company_name:
                raise forms.ValidationError("Please provide a company name.")
            if (
                company_name
                and Tenant.objects.filter(name__iexact=company_name).exists()
            ):
                raise forms.ValidationError(
                    f"Company '{company_name}' already exists. Please join it or choose a different name."
                )

        return cleaned_data

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match. Please re-enter.")
            if password1.lower() in ["password", "123456", "qwerty", "letmein"]:
                raise forms.ValidationError(
                    "This password is too common. Please choose a stronger password."
                )
            if len(password1) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long."
                )
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        registration_type = self.cleaned_data.get("registration_type")

        if registration_type == "create":
            # Create new tenant/company
            company_name = self.cleaned_data["company_name"]
            subdomain = company_name.lower().replace(" ", "-").replace("_", "-")[:50]

            # Ensure unique subdomain
            base_subdomain = subdomain
            counter = 1
            while Tenant.objects.filter(subdomain=subdomain).exists():
                subdomain = f"{base_subdomain}-{counter}"
                counter += 1

            tenant = Tenant.objects.create(
                name=company_name,
                subdomain=subdomain,
                specialization=self.cleaned_data.get(
                    "specialization", "general_practice"
                ),
                plan="free_trial",
                trial_started_at=timezone.now(),
                trial_ended_at=timezone.now() + timedelta(days=14),
                is_active=True,
            )

            user.tenant = tenant
            user.role = "admin"  # First user in new company becomes admin
            user.is_active = True  # Auto-activate company creator
        else:
            # Join existing tenant
            user.tenant = self.cleaned_data["tenant"]
            user.role = self.cleaned_data.get("role", "user")
            user.is_active = (
                False  # Require admin approval when joining existing company
            )

        if commit:
            user.save()
        return user
