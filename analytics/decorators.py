"""
Analytics access control decorators.
Restricts analytics features to Professional and Enterprise subscriptions only.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def subscription_required(*allowed_plans):
    """
    Decorator to restrict access to specific subscription plans.
    Usage: @subscription_required('professional', 'enterprise')
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            tenant = request.user.tenant

            # Check if tenant has required plan
            if tenant.plan not in allowed_plans:
                messages.error(
                    request,
                    f"Analytics features are only available for Professional and Enterprise plans. "
                    f"Your current plan is '{tenant.get_plan_display()}'. "
                    f"Please upgrade to access advanced analytics.",
                )
                return redirect("view_plans")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def analytics_access_required(view_func):
    """
    Convenience decorator for analytics-specific access control.
    Restricts to Professional and Enterprise plans only.
    """
    return subscription_required("professional", "enterprise")(view_func)


def admin_or_analytics_access(view_func):
    """
    Decorator that requires user to be admin AND have analytics subscription.
    """

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        tenant = user.tenant

        # Check if user is admin
        if not (user.is_superuser or getattr(user, "role", None) == "admin"):
            messages.error(request, "You must be an administrator to access analytics.")
            return redirect("dashboard")

        # Check if tenant has analytics subscription
        if tenant.plan not in ("professional", "enterprise"):
            messages.error(
                request,
                f"Analytics features are only available for Professional and Enterprise plans. "
                f"Your current plan is '{tenant.get_plan_display()}'. "
                f"Please upgrade to access advanced analytics.",
            )
            return redirect("view_plans")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
