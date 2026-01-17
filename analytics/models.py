from django.db import models

from tenants.models import Tenant


class AnalyticsEvent(models.Model):
    """
    Tracks system events for analytics and reporting.
    Automatically captures user actions across the platform.
    """

    EVENT_TYPES = [
        ("login", "User Login"),
        ("logout", "User Logout"),
        ("patient_view", "Patient View"),
        ("patient_create", "Patient Create"),
        ("patient_edit", "Patient Edit"),
        ("appointment_create", "Appointment Create"),
        ("appointment_edit", "Appointment Edit"),
        ("appointment_cancel", "Appointment Cancel"),
        ("clinical_record_create", "Clinical Record Create"),
        ("clinical_record_view", "Clinical Record View"),
        ("lab_result_create", "Lab Result Create"),
        ("lab_result_view", "Lab Result View"),
        ("document_upload", "Document Upload"),
        ("referral_create", "Referral Create"),
        ("payment_received", "Payment Received"),
        ("report_generated", "Report Generated"),
        ("other", "Other Event"),
    ]

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="analytics_events"
    )
    event_type = models.CharField(max_length=64, choices=EVENT_TYPES, db_index=True)
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(
        blank=True, null=True, help_text="Additional event data (JSON format)"
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["tenant", "event_type", "timestamp"]),
            models.Index(fields=["tenant", "user_id", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} at {self.timestamp} (tenant {self.tenant_id})"
