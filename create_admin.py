#!/usr/bin/env python
"""
Simple script to create a superuser in a multi-tenant context.
Usage: python create_admin.py
"""
import os
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from tenants.models import Tenant

User = get_user_model()

# Create or get default tenant
tenant, created = Tenant.objects.get_or_create(
    name="DefaultTenant",
    defaults={
        "subdomain": "default",
        "plan": "free_trial",
        "trial_started_at": timezone.now(),
        "trial_ended_at": timezone.now() + timedelta(days=14),
        "is_active": True,
    },
)

if created:
    print(f"✓ Created default tenant: {tenant.name}")
else:
    print(f"✓ Using existing tenant: {tenant.name}")

# Create superuser
username = "admin"
email = "admin@healthcare-saas.com"
password = "AdminPass123"

if User.objects.filter(username=username).exists():
    print(f"✗ User with username '{username}' already exists")
else:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        tenant=tenant,
    )
    user.platform_admin = True
    user.save()

    print("\n✓ Successfully created superuser:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Tenant: {user.tenant.name}")
    print("  Platform Admin: True")
    print("\nYou can now login at: /admin/")
