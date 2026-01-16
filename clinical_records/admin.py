
from django.contrib import admin
from .models import ClinicalRecord

@admin.register(ClinicalRecord)
class ClinicalRecordAdmin(admin.ModelAdmin):
	list_display = ("id", "patient", "note_type", "tenant", "created_at")
	list_filter = ("note_type", "tenant", "created_at")
	search_fields = ("patient__first_name", "patient__last_name", "note_type", "tenant__name")
	readonly_fields = ("created_at", "updated_at", "tenant")
	fieldsets = (
		("Patient Info", {
			"fields": ("tenant", "patient")
		}),
		("Note Details", {
			"fields": ("note_type", "note")
		}),
		("Metadata", {
			"fields": ("created_at", "updated_at"),
			"classes": ("collapse",)
		}),
	)
	
	def save_model(self, request, obj, form, change):
		if not change:  # New object
			obj.tenant = request.user.tenant
		super().save_model(request, obj, form, change)
