
from django.contrib import admin
from .models import Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "subdomain", "specialization", "plan", "is_active", "created_at")
	list_filter = ("specialization", "plan", "is_active", "created_at")
	search_fields = ("name", "subdomain")
	readonly_fields = ("created_at", "updated_at")
	fieldsets = (
		("Tenant Info", {
			"fields": ("name", "subdomain", "specialization")
		}),
		("Billing", {
			"fields": ("plan", "stripe_customer_id", "stripe_subscription_id", "trial_started_at", "trial_ended_at")
		}),
		("Status", {
			"fields": ("is_active",)
		}),
		("Metadata", {
			"fields": ("created_at", "updated_at"),
			"classes": ("collapse",)
		}),
	)
