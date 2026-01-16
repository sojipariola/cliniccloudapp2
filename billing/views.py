from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tenants.models import Tenant
from billing.constants import PLAN_DETAILS

@login_required
def billing_dashboard(request):
    user = request.user
    is_platform_admin = getattr(user, "platform_admin", False)

    if is_platform_admin:
        tenants = Tenant.objects.all().prefetch_related("users")

        tenant_rows = []
        for tenant in tenants:
            users = list(tenant.users.all())
            primary_admin = next(
                (u for u in users if u.platform_admin or u.is_superuser),
                next((u for u in users if u.is_staff), None),
            ) or (users[0] if users else None)

            tenant_rows.append({
                "tenant": tenant,
                "primary_admin": primary_admin,
                "contact_email": primary_admin.email if primary_admin else "",
                "plan": tenant.plan,
                "stripe_customer_id": tenant.stripe_customer_id,
                "stripe_subscription_id": tenant.stripe_subscription_id,
                "trial": {
                    "is_free_trial": tenant.plan == "free_trial",
                    "trial_days_remaining": tenant.trial_days_remaining() if hasattr(tenant, "trial_days_remaining") else None,
                },
            })

        context = {
            "is_platform_admin": True,
            "tenant_rows": tenant_rows,
        }
        return render(request, "billing/dashboard.html", context)

    tenant = user.tenant
    plan_info = PLAN_DETAILS.get(tenant.plan, {})
    primary_admin = user if user.is_staff else None
    context = {
        "is_platform_admin": False,
        "tenant": tenant,
        "plan_info": plan_info,
        "stripe_customer_id": tenant.stripe_customer_id,
        "stripe_subscription_id": tenant.stripe_subscription_id,
        "trial": {
            "is_free_trial": tenant.plan == "free_trial",
            "trial_days_remaining": tenant.trial_days_remaining() if hasattr(tenant, "trial_days_remaining") else None,
        },
        "primary_admin": primary_admin,
    }
    return render(request, "billing/dashboard.html", context)
