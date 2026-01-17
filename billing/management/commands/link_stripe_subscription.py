"""
Management command to link a Stripe customer/subscription to a tenant.
Usage: python manage.py link_stripe_subscription <tenant_id> <stripe_customer_id> <stripe_subscription_id> <plan>
"""
from django.core.management.base import BaseCommand

from billing.constants import PLAN_DETAILS
from tenants.models import Tenant


class Command(BaseCommand):
    help = "Link a Stripe customer and subscription to a tenant"

    def add_arguments(self, parser):
        parser.add_argument("tenant_id", type=int, help="Tenant ID")
        parser.add_argument(
            "stripe_customer_id", type=str, help="Stripe customer ID (cus_...)"
        )
        parser.add_argument(
            "stripe_subscription_id", type=str, help="Stripe subscription ID (sub_...)"
        )
        parser.add_argument(
            "plan", type=str, choices=list(PLAN_DETAILS.keys()), help="Plan name"
        )

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        stripe_customer_id = options["stripe_customer_id"]
        stripe_subscription_id = options["stripe_subscription_id"]
        plan = options["plan"]

        try:
            tenant = Tenant.objects.get(id=tenant_id)
            tenant.stripe_customer_id = stripe_customer_id
            tenant.stripe_subscription_id = stripe_subscription_id
            tenant.plan = plan
            tenant.trial_ended_at = None  # Clear trial
            tenant.save(
                update_fields=[
                    "stripe_customer_id",
                    "stripe_subscription_id",
                    "plan",
                    "trial_ended_at",
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully linked tenant "{tenant.name}" (ID: {tenant_id}) to:\n'
                    f"  Customer: {stripe_customer_id}\n"
                    f"  Subscription: {stripe_subscription_id}\n"
                    f"  Plan: {plan}"
                )
            )
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Tenant with ID {tenant_id} does not exist")
            )
