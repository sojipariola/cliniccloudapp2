import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from tenants.models import Tenant
from billing.constants import PLAN_DETAILS, PRICE_TO_PLAN

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@require_POST
def create_checkout_session(request):
    """Create a Stripe Checkout session for a subscription."""
    price_id = request.POST.get("price_id")
    plan = PRICE_TO_PLAN.get(price_id)

    if not plan or plan not in PLAN_DETAILS:
        messages.error(request, "Invalid plan selection.")
        return redirect("view_plans")

    tenant = request.user.tenant
    if not tenant:
        messages.error(request, "No tenant associated with your account.")
        return redirect("dashboard")

    # Ensure customer exists
    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            name=tenant.name,
            metadata={"tenant_id": tenant.id},
        )
        tenant.stripe_customer_id = customer.id
        tenant.save(update_fields=["stripe_customer_id"])

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=tenant.stripe_customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=request.build_absolute_uri(reverse("upgrade_success")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("view_plans")),
        metadata={"plan": plan, "tenant_id": str(tenant.id)},
    )

    return redirect(session.url, code=303)


@login_required
@require_POST
def create_portal_session(request):
    """Create a Stripe Billing Portal session for the tenant's customer."""
    tenant = request.user.tenant
    if not tenant or not tenant.stripe_customer_id:
        messages.error(request, "No Stripe customer found for your account.")
        return redirect("billing_dashboard")

    portal_session = stripe.billing_portal.Session.create(
        customer=tenant.stripe_customer_id,
        return_url=request.build_absolute_uri(reverse("billing_dashboard")),
    )

    return redirect(portal_session.url)
