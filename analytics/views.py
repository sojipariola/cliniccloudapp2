import json
from datetime import timedelta

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.shortcuts import render
from django.utils import timezone

from appointments.models import Appointment
from billing.models import Payment
from clinical_records.models import ClinicalRecord
from labs.models import LabResult
from patients.models import Patient
from users.models import CustomUser

from .decorators import admin_or_analytics_access
from .models import AnalyticsEvent


@admin_or_analytics_access
def analytics_dashboard(request):
    """
    Main analytics dashboard with comprehensive business intelligence.
    Only accessible to admins with Professional or Enterprise subscriptions.
    """
    tenant = request.user.tenant
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)

    # Key Performance Indicators (KPIs)
    context = {
        "tenant": tenant,
        "plan": tenant.get_plan_display(),
        # Patient Metrics
        "total_patients": Patient.objects.filter(tenant=tenant).count(),
        "new_patients_30d": Patient.objects.filter(
            tenant=tenant, created_at__gte=timezone.now() - timedelta(days=30)
        ).count(),
        "active_patients_90d": Patient.objects.filter(
            tenant=tenant,
            appointments__scheduled_for__gte=timezone.now() - timedelta(days=90),
        )
        .distinct()
        .count(),
        # Appointment Metrics
        "total_appointments": Appointment.objects.filter(tenant=tenant).count(),
        "appointments_this_month": Appointment.objects.filter(
            tenant=tenant,
            scheduled_for__month=today.month,
            scheduled_for__year=today.year,
        ).count(),
        "upcoming_appointments": Appointment.objects.filter(
            tenant=tenant, scheduled_for__gte=timezone.now(), status="scheduled"
        ).count(),
        "completed_appointments_30d": Appointment.objects.filter(
            tenant=tenant,
            scheduled_for__gte=timezone.now() - timedelta(days=30),
            status="completed",
        ).count(),
        # Clinical Records Metrics
        "total_clinical_records": ClinicalRecord.objects.filter(tenant=tenant).count(),
        "records_this_month": ClinicalRecord.objects.filter(
            tenant=tenant, created_at__month=today.month, created_at__year=today.year
        ).count(),
        # Lab Results Metrics
        "total_lab_results": LabResult.objects.filter(tenant=tenant).count(),
        # User Activity Metrics
        "total_users": CustomUser.objects.filter(tenant=tenant, is_active=True).count(),
        "admin_count": CustomUser.objects.filter(
            tenant=tenant, role="admin", is_active=True
        ).count(),
    }

    # Revenue Analytics (if applicable)
    revenue_data = Payment.objects.filter(
        tenant=tenant, timestamp__gte=timezone.now() - timedelta(days=90)
    ).aggregate(
        total_revenue=Sum("amount"),
        avg_payment=Avg("amount"),
        payment_count=Count("id"),
    )
    context.update(revenue_data)

    return render(request, "analytics/dashboard.html", context)


@admin_or_analytics_access
def patient_analytics(request):
    """Patient demographics and growth analytics."""
    tenant = request.user.tenant

    # Patient growth over time (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    patient_growth = (
        Patient.objects.filter(tenant=tenant, created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # Convert to chart-friendly format
    growth_labels = [item["month"].strftime("%b %Y") for item in patient_growth]
    growth_data = [item["count"] for item in patient_growth]

    # Age distribution (if date_of_birth exists)
    age_ranges = [
        ("0-18", 0, 18),
        ("19-35", 19, 35),
        ("36-50", 36, 50),
        ("51-65", 51, 65),
        ("65+", 66, 150),
    ]

    age_distribution = []
    for label, min_age, max_age in age_ranges:
        cutoff_max = timezone.now().date() - timedelta(days=min_age * 365)
        cutoff_min = timezone.now().date() - timedelta(days=max_age * 365)
        count = Patient.objects.filter(
            tenant=tenant, date_of_birth__lte=cutoff_max, date_of_birth__gte=cutoff_min
        ).count()
        age_distribution.append({"label": label, "count": count})

    context = {
        "patient_growth_labels": json.dumps(growth_labels),
        "patient_growth_data": json.dumps(growth_data),
        "age_distribution": age_distribution,
        "total_patients": Patient.objects.filter(tenant=tenant).count(),
    }

    return render(request, "analytics/patient_analytics.html", context)


@admin_or_analytics_access
def appointment_analytics(request):
    """Appointment scheduling patterns and efficiency metrics."""
    tenant = request.user.tenant

    # Appointments by status
    status_distribution = (
        Appointment.objects.filter(tenant=tenant)
        .values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Appointments by day of week (last 90 days)
    ninety_days_ago = timezone.now() - timedelta(days=90)
    appointments_by_day = []
    for day_num in range(7):
        day_name = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ][day_num]
        count = Appointment.objects.filter(
            tenant=tenant,
            scheduled_for__gte=ninety_days_ago,
            scheduled_for__week_day=(day_num + 2) % 7
            + 1,  # Django week_day: Sunday=1
        ).count()
        appointments_by_day.append({"day": day_name, "count": count})

    # Monthly appointment trends (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_appointments = (
        Appointment.objects.filter(
            tenant=tenant, scheduled_for__gte=twelve_months_ago
        )
        .annotate(month=TruncMonth("scheduled_for"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    monthly_labels = [item["month"].strftime("%b %Y") for item in monthly_appointments]
    monthly_data = [item["count"] for item in monthly_appointments]

    # Appointment types (if appointment_type field exists)
    type_distribution = (
        Appointment.objects.filter(tenant=tenant)
        .values("appointment_type")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )  # Top 10 types

    context = {
        "status_distribution": status_distribution,
        "appointments_by_day": appointments_by_day,
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
        "type_distribution": type_distribution,
        "total_appointments": Appointment.objects.filter(tenant=tenant).count(),
    }

    return render(request, "analytics/appointment_analytics.html", context)


@admin_or_analytics_access
def revenue_analytics(request):
    """Financial performance and revenue analytics."""
    tenant = request.user.tenant

    # Monthly revenue (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_revenue = (
        Payment.objects.filter(tenant=tenant, timestamp__gte=twelve_months_ago)
        .annotate(month=TruncMonth("timestamp"))
        .values("month")
        .annotate(revenue=Sum("amount"))
        .order_by("month")
    )

    revenue_labels = [item["month"].strftime("%b %Y") for item in monthly_revenue]
    revenue_data = [float(item["revenue"]) for item in monthly_revenue]

    # Payment method distribution
    payment_methods = (
        Payment.objects.filter(tenant=tenant)
        .values("currency")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )

    # Revenue by patient (top 10)
    top_patients = (
        Payment.objects.filter(tenant=tenant, patient__isnull=False)
        .values("patient__first_name", "patient__last_name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:10]
    )

    # Key metrics
    total_revenue = (
        Payment.objects.filter(tenant=tenant).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    avg_payment = (
        Payment.objects.filter(tenant=tenant).aggregate(Avg("amount"))["amount__avg"]
        or 0
    )

    context = {
        "revenue_labels": json.dumps(revenue_labels),
        "revenue_data": json.dumps(revenue_data),
        "payment_methods": payment_methods,
        "top_patients": top_patients,
        "total_revenue": total_revenue,
        "avg_payment": avg_payment,
        "payment_count": Payment.objects.filter(tenant=tenant).count(),
    }

    return render(request, "analytics/revenue_analytics.html", context)


@admin_or_analytics_access
def user_activity_analytics(request):
    """User activity and system usage analytics."""
    tenant = request.user.tenant

    # Activity events by type
    event_counts = (
        AnalyticsEvent.objects.filter(tenant=tenant)
        .values("event_type")
        .annotate(count=Count("id"))
        .order_by("-count")[:15]
    )

    # User activity ranking
    user_activity = (
        AnalyticsEvent.objects.filter(tenant=tenant, user_id__isnull=False)
        .values("user_id")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    users = {
        u.id: u
        for u in CustomUser.objects.filter(
            id__in=[ua["user_id"] for ua in user_activity]
        )
    }

    # Activity timeline (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_activity = (
        AnalyticsEvent.objects.filter(tenant=tenant, timestamp__gte=thirty_days_ago)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    activity_labels = [item["day"].strftime("%b %d") for item in daily_activity]
    activity_data = [item["count"] for item in daily_activity]

    context = {
        "event_counts": event_counts,
        "user_activity": user_activity,
        "users": users,
        "activity_labels": json.dumps(activity_labels),
        "activity_data": json.dumps(activity_data),
        "total_events": AnalyticsEvent.objects.filter(tenant=tenant).count(),
    }

    return render(request, "analytics/user_activity_analytics.html", context)


@admin_or_analytics_access
def executive_summary(request):
    """
    Executive summary with high-level KPIs and insights.
    Perfect for C-suite and board presentations.
    """
    tenant = request.user.tenant
    today = timezone.now().date()

    # Time periods
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    current_quarter_start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
    current_year_start = today.replace(month=1, day=1)

    # Patient Growth Metrics
    patients_current_month = Patient.objects.filter(
        tenant=tenant, created_at__gte=current_month_start
    ).count()
    patients_last_month = Patient.objects.filter(
        tenant=tenant,
        created_at__gte=last_month_start,
        created_at__lt=current_month_start,
    ).count()
    patient_growth_rate = (
        ((patients_current_month - patients_last_month) / patients_last_month * 100)
        if patients_last_month > 0
        else 0
    )

    # Revenue Metrics
    revenue_current_month = (
        Payment.objects.filter(
            tenant=tenant, timestamp__gte=current_month_start
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )

    revenue_last_month = (
        Payment.objects.filter(
            tenant=tenant,
            timestamp__gte=last_month_start,
            timestamp__lt=current_month_start,
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )

    revenue_growth_rate = (
        ((revenue_current_month - revenue_last_month) / revenue_last_month * 100)
        if revenue_last_month > 0
        else 0
    )

    # Appointment Efficiency
    completed_appointments = Appointment.objects.filter(
        tenant=tenant, scheduled_for__gte=current_month_start, status="completed"
    ).count()

    total_appointments = Appointment.objects.filter(
        tenant=tenant, scheduled_for__gte=current_month_start
    ).count()

    completion_rate = (
        (completed_appointments / total_appointments * 100)
        if total_appointments > 0
        else 0
    )

    # System Usage
    active_users = CustomUser.objects.filter(
        tenant=tenant,
        is_active=True,
        last_login__gte=timezone.now() - timedelta(days=30),
    ).count()

    context = {
        "patients_current_month": patients_current_month,
        "patient_growth_rate": round(patient_growth_rate, 1),
        "revenue_current_month": revenue_current_month,
        "revenue_growth_rate": round(revenue_growth_rate, 1),
        "completion_rate": round(completion_rate, 1),
        "active_users": active_users,
        "total_patients": Patient.objects.filter(tenant=tenant).count(),
        "total_revenue_ytd": Payment.objects.filter(
            tenant=tenant, timestamp__gte=current_year_start
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0,
    }

    return render(request, "analytics/executive_summary.html", context)
