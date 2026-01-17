import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from billing.constants import PLAN_DETAILS
from tenants.models import Tenant

stripe.api_key = settings.STRIPE_SECRET_KEY


def _stripe_key_valid(key: str) -> bool:
    """Basic validation to avoid common misconfigurations without exposing secrets."""
    if not isinstance(key, str) or not key:
        return False
    if "here" in key.lower():  # placeholder like sk_test_****here
        return False
    if not (key.startswith("sk_test_") or key.startswith("sk_live_")):
        return False
    return len(key) > 20


@login_required
@require_http_methods(["GET", "POST"])
def upgrade_plan(request, plan):
    """Initiate upgrade to a paid plan via Stripe."""
    tenant = request.user.tenant

    if not tenant:
        messages.error(request, "No tenant associated with your account.")
        return redirect("dashboard")

    if plan not in PLAN_DETAILS:
        messages.error(request, "Invalid plan selected.")
        return redirect("view_plans")

    plan_info = PLAN_DETAILS[plan]

    # Fail fast if Stripe secret key looks invalid/missing
    if not _stripe_key_valid(settings.STRIPE_SECRET_KEY):
        messages.error(
            request,
            (
                "Payment is not configured: invalid Stripe secret key. "
                "Set STRIPE_SECRET_KEY in your environment (.env) with a valid test/live secret key."
            ),
        )
        return redirect("view_plans")

    if request.method == "GET":
        context = {
            "plan": plan,
            "plan_info": plan_info,
            "tenant": tenant,
        }
        return render(request, "billing/upgrade_confirm.html", context)

    # POST: Create Stripe checkout session
    try:
        # Create or get Stripe customer
        if not tenant.stripe_customer_id:
            customer = stripe.Customer.create(
                name=tenant.name, metadata={"tenant_id": tenant.id}
            )
            tenant.stripe_customer_id = customer.id
            tenant.save()

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=tenant.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan_info["stripe_price_id"],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.build_absolute_uri(
                "/billing/upgrade-success/?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=request.build_absolute_uri("/billing/upgrade-cancel/"),
            metadata={"plan": plan, "tenant_id": tenant.id},
        )

        return redirect(session.url, code=303)

    except stripe.error.StripeError as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect("view_plans")


@login_required
@require_http_methods(["GET"])
def upgrade_success(request):
    """Handle successful upgrade."""
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(request, "Invalid session.")
        return redirect("view_plans")

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        # Update tenant subscription
        with transaction.atomic():
            tenant = request.user.tenant
            plan = session.metadata.get("plan")

            if plan in PLAN_DETAILS:
                tenant.plan = plan
                tenant.stripe_subscription_id = session.subscription
                tenant.trial_ended_at = None  # End trial
                tenant.save()

                messages.success(
                    request,
                    f"Congratulations! You've upgraded to {PLAN_DETAILS[plan]['name']}.",
                )

        context = {
            "session_id": session_id,
            "plan": plan,
            "plan_info": PLAN_DETAILS.get(plan, {}),
        }
        return render(request, "billing/success.html", context)

    except stripe.error.StripeError as e:
        messages.error(request, f"Error processing upgrade: {str(e)}")
        return redirect("view_plans")


@login_required
@require_http_methods(["GET"])
def upgrade_cancel(request):
    """Handle cancelled upgrade."""
    context = {}
    return render(request, "billing/cancel.html", context)
