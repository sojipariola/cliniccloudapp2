from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
        "email",
        "phone",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("gender", "created_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("tenant", "first_name", "last_name", "date_of_birth")
        }),
        ("Demographics & Picture", {
            "fields": ("gender", "picture"),
        }),
        ("Contact Information", {
            "fields": ("email", "phone"),
        }),
    )
