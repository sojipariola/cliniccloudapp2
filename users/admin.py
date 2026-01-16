
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser
from common.audit import log_audit

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "tenant", "role", "platform_admin", "is_active", "is_staff", "activate_link")
    list_filter = ("platform_admin", "is_active", "is_staff", "is_superuser", "role")
    search_fields = ("username", "email", "tenant__name", "role")
    actions = ["activate_users", "deactivate_users", "grant_platform_admin", "revoke_platform_admin"]
    
    def activate_link(self, obj):
        if not obj.is_active:
            url = reverse('approve_user', args=[obj.pk])
            return format_html(
                '<a href="{}" style="background:#10b981;color:#fff;padding:4px 12px;border-radius:4px;text-decoration:none;font-weight:600;">Activate</a>',
                url
            )
        return format_html('<span style="color:#10b981;font-weight:600;">{}</span>', '✓ Active')
    activate_link.short_description = "Activation"
    
    def activate_users(self, request, queryset):
        inactive_users = queryset.filter(is_active=False)
        count = inactive_users.count()
        for user in inactive_users:
            user.is_active = True
            user.save()
            log_audit("user_approved", user=user, tenant=user.tenant, 
                     details=f"User {user.username} approved by {request.user.username} via admin action.")
        self.message_user(request, f"{count} user(s) successfully activated.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        active_users = queryset.filter(is_active=True)
        count = active_users.count()
        for user in active_users:
            user.is_active = False
            user.save()
            log_audit("user_deactivated", user=user, tenant=user.tenant,
                      details=f"User {user.username} deactivated by {request.user.username} via admin action.")
        self.message_user(request, f"{count} user(s) successfully deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

    def grant_platform_admin(self, request, queryset):
        updated = 0
        for user in queryset:
            if not user.platform_admin:
                user.platform_admin = True
                user.is_staff = True  # ensure access to admin UI
                user.save()
                log_audit("platform_admin_granted", user=user, tenant=user.tenant,
                          details=f"Platform admin granted to {user.username} by {request.user.username} via admin action.")
                updated += 1
        self.message_user(request, f"{updated} user(s) promoted to ClinicCloud platform admin.")
    grant_platform_admin.short_description = "Grant platform admin (ClinicCloud)"

    def revoke_platform_admin(self, request, queryset):
        updated = 0
        for user in queryset:
            if user.platform_admin:
                user.platform_admin = False
                user.save()
                log_audit("platform_admin_revoked", user=user, tenant=user.tenant,
                          details=f"Platform admin revoked for {user.username} by {request.user.username} via admin action.")
                updated += 1
        self.message_user(request, f"{updated} user(s) demoted from ClinicCloud platform admin.")
    revoke_platform_admin.short_description = "Revoke platform admin (ClinicCloud)"
