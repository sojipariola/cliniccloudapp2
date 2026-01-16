from django.db import models
from django.utils import timezone

class Tenant(models.Model):
    PLAN_CHOICES = [
        ('free_trial', 'Free Trial'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('general_practice', 'General Practice'),
        ('pediatrics', 'Pediatrics'),
        ('dental', 'Dental'),
        ('eye', 'Ophthalmology'),
        ('womens_health', 'Women\'s Health'),
        ('dermatology', 'Dermatology'),
        ('mental_health', 'Mental Health'),
        ('physiotherapy', 'Physiotherapy'),
        ('orthopedic', 'Orthopedic Surgery'),
        ('cardiology', 'Cardiology'),
        ('ent', 'Ear, Nose & Throat'),
        ('urology', 'Urology'),
        ('oncology', 'Oncology'),
        ('allergy', 'Allergy & Immunology'),
        ('pain', 'Pain Management'),
        ('gastroenterology', 'Gastroenterology'),
        ('endocrinology', 'Endocrinology'),
        ('neurology', 'Neurology'),
        ('surgical', 'General Surgery'),
        ('urgent_care', 'Urgent Care'),
        ('multi_specialty', 'Multi-Specialty'),
        ('telemedicine', 'Telemedicine'),
        ('community_health', 'Community Health'),
        ('fertility', 'Fertility Clinic'),
        ('geriatric', 'Geriatric Care'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    subdomain = models.CharField(max_length=50, unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free_trial')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='general_practice')
    trial_started_at = models.DateTimeField(null=True, blank=True)
    trial_ended_at = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_plan_display()})"
    
    def is_free_trial(self):
        """Check if tenant is in active free trial."""
        if self.plan != 'free_trial':
            return False
        if self.trial_ended_at is None:
            return False
        return timezone.now() < self.trial_ended_at
    
    def trial_days_remaining(self):
        """Calculate remaining trial days."""
        if not self.is_free_trial():
            return 0
        delta = self.trial_ended_at - timezone.now()
        return max(0, delta.days)
    
    def can_upgrade(self):
        """Check if tenant can upgrade."""
        return self.plan == 'free_trial' and self.is_free_trial()

