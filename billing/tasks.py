import logging

from celery import shared_task
from django.utils import timezone

from billing.free_trial import (
    is_tenant_in_free_trial,
    free_trial_days_left,
    send_trial_expiry_notification,
)
from tenants.models import Tenant


logger = logging.getLogger(__name__)

@shared_task
def weekly_trial_expiry_notifications():
    for tenant in Tenant.objects.all():
        if is_tenant_in_free_trial(tenant):
            days_left = free_trial_days_left(tenant)
            if days_left <= 21:  # Notify in last 3 weeks
                send_trial_expiry_notification(tenant)
                logger.info("Sent weekly trial expiry notification", extra={"tenant_id": tenant.id, "days_left": days_left})


@shared_task
def daily_trial_expiry_soft_reminder():
    """Lightweight daily reminder when trials are close to ending."""
    notified = 0
    for tenant in Tenant.objects.all():
        if is_tenant_in_free_trial(tenant):
            days_left = free_trial_days_left(tenant)
            if 0 < days_left <= 7:
                send_trial_expiry_notification(tenant)
                notified += 1
    logger.info("Daily trial reminders processed", extra={"notified": notified})
    return {"notified": notified}


@shared_task
def nightly_subscription_health_check():
    """Log basic subscription health metrics for observability."""
    plans = {plan: 0 for plan, _ in Tenant.PLAN_CHOICES}
    for tenant in Tenant.objects.all():
        plans[tenant.plan] = plans.get(tenant.plan, 0) + 1
    logger.info("Subscription mix", extra={"plans": plans, "timestamp": timezone.now().isoformat()})
    return plans
