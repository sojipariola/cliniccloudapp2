from django.db import models

from tenants.models import Tenant


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="patients"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text="Patient's gender for medical records"
    )
    picture = models.ImageField(
        upload_to="patient_pictures/",
        blank=True,
        null=True,
        help_text="Patient's profile picture"
    )
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_profile_picture_url(self):
        """Get profile picture URL, with gender-based default fallback.
        
        If patient has uploaded a custom picture, use that.
        If patient disclosed gender (M or F), use gender-specific default.
        Otherwise (no gender, Other, or Prefer not to say), use neutral default.
        """
        if self.picture:
            return self.picture.url
        
        # Return gender-specific default only if gender is disclosed
        if self.gender == 'M':
            return '/static/img/male_default_profile.png'
        elif self.gender == 'F':
            return '/static/img/female_default_profile.png'
        else:
            # No gender disclosed (None, blank, 'O', or 'P') → use neutral default
            return '/static/img/default_profile.png'
