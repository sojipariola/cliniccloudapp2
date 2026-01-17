import json

import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from billing.constants import PLAN_DETAILS
from tenants.models import Tenant

stripe.api_key = settings.STRIPE_SECRET_KEY


def _webhook_secret_valid(secret: str) -> bool:
    if not isinstance(secret, str) or not secret:
        return False
    if "here" in secret.lower():
        return False
    # Stripe webhook signing secrets typically start with 'whsec_'
    return secret.startswith("whsec_") and len(secret) > 20


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not _webhook_secret_valid(webhook_secret):
        # Misconfigured webhook secret; fail clearly for visibility
        return HttpResponse("Webhook not configured", status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse("Invalid signature", status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {}) or {}
        plan = metadata.get("plan")
        tenant_id = metadata.get("tenant_id")
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")

        if plan and tenant_id and plan in PLAN_DETAILS:
            try:
                with transaction.atomic():
                    tenant = Tenant.objects.select_for_update().get(id=tenant_id)
                    tenant.plan = plan
                    tenant.stripe_subscription_id = subscription_id
                    if customer_id and not tenant.stripe_customer_id:
                        tenant.stripe_customer_id = customer_id
                    tenant.trial_ended_at = None
                    tenant.save(
                        update_fields=[
                            "plan",
                            "stripe_subscription_id",
                            "stripe_customer_id",
                            "trial_ended_at",
                        ]
                    )
            except Tenant.DoesNotExist:
                pass

    return HttpResponse(status=200)
