from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from tenants.models import Tenant
from tenants.forms import TenantCreationForm
from billing.constants import TRIAL_DAYS, PLAN_DETAILS

User = get_user_model()

@require_http_methods(["GET", "POST"])
def create_tenant(request):
    """Create a new tenant organization (starts with free trial)."""
    if request.method == 'POST':
        form = TenantCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create tenant with free trial
                tenant = form.save(commit=False)
                tenant.plan = 'free_trial'
                tenant.trial_started_at = timezone.now()
                tenant.trial_ended_at = timezone.now() + timedelta(days=TRIAL_DAYS)
                tenant.save()
                
                messages.success(
                    request, 
                    f"Welcome! Your organization '{tenant.name}' has been created. "
                    f"You have {TRIAL_DAYS} days of free trial access."
                )
                
                # Redirect to onboarding
                return redirect('tenant_onboarding', tenant_id=tenant.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TenantCreationForm()
    
    context = {
        'form': form,
        'plan_details': PLAN_DETAILS['free_trial'],
        'trial_days': TRIAL_DAYS,
    }
    return render(request, 'tenants/create_tenant.html', context)

@login_required
@require_http_methods(["GET"])
def tenant_onboarding(request, tenant_id):
    """Onboarding page for new tenants (shows what's included in free trial)."""
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        messages.error(request, "Tenant not found.")
        return redirect('dashboard')
    
    # Verify user can access this tenant
    if not request.user.tenant or request.user.tenant.id != tenant.id:
        messages.error(request, "You don't have access to this tenant.")
        return redirect('dashboard')
    
    context = {
        'tenant': tenant,
        'trial_days': tenant.trial_days_remaining(),
        'free_plan': PLAN_DETAILS['free_trial'],
    }
    return render(request, 'tenants/onboarding.html', context)

@login_required
@require_http_methods(["GET"])
def view_plans(request):
    """Display all available plans for upgrade."""
    if not request.user.tenant:
        messages.error(request, "No tenant associated with your account.")
        return redirect('dashboard')
    
    context = {
        'tenant': request.user.tenant,
        'plans': PLAN_DETAILS,
        'current_plan': request.user.tenant.plan,
    }
    return render(request, 'billing/plans.html', context)

