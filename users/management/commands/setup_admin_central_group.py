from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create or update an 'Admin Central' group with comprehensive admin permissions "
        "for managing users, patients, appointments, clinical records, labs, billing, and more."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what permissions would be granted without creating the group",
        )
        parser.add_argument(
            "--assign-role",
            help="Automatically add all users with this role (case-insensitive) to the group after creation",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        assign_role = options.get("assign_role")

        # Define comprehensive permissions for Admin Central
        permission_specs = [
            # Users app - full control
            ("users", "customuser", ["view", "add", "change", "delete"]),
            # Patients app - full control
            ("patients", "patient", ["view", "add", "change", "delete"]),
            # Appointments app - full control
            ("appointments", "appointment", ["view", "add", "change", "delete"]),
            # Clinical records - full control
            ("clinical_records", "clinicalrecord", ["view", "add", "change", "delete"]),
            # Labs - full control
            ("labs", "labresult", ["view", "add", "change", "delete"]),
            # Documents - full control
            ("documents", "document", ["view", "add", "change", "delete"]),
            # Referrals - full control
            ("referrals", "referral", ["view", "add", "change", "delete"]),
            ("referrals", "clinic", ["view", "add", "change", "delete"]),
            # Billing - view/change (not delete)
            ("billing", "tenantsubscription", ["view", "change"]),
            ("billing", "subscriptionplan", ["view"]),
            ("billing", "payment", ["view"]),
            # Audit logs - view only
            ("audit_logs", "auditlog", ["view"]),
            # Analytics - view
            ("analytics", "analyticsevent", ["view"]),
            # Tenants - view/change (not create/delete for safety)
            ("tenants", "tenant", ["view", "change"]),
        ]

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN: Would create 'Admin Central' group with the following permissions:"
                )
            )
            for app_label, model_name, actions in permission_specs:
                for action in actions:
                    self.stdout.write(f"  - {app_label}.{action}_{model_name}")
            return

        # Create or get the group
        group, created = Group.objects.get_or_create(name="Admin Central")
        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created 'Admin Central' group")
            )
        else:
            self.stdout.write(
                "✓ 'Admin Central' group already exists, updating permissions..."
            )

        # Clear existing permissions to avoid stale entries
        group.permissions.clear()

        # Add permissions
        added_count = 0
        for app_label, model_name, actions in permission_specs:
            try:
                content_type = ContentType.objects.get(
                    app_label=app_label, model=model_name
                )
                for action in actions:
                    codename = f"{action}_{model_name}"
                    try:
                        permission = Permission.objects.get(
                            content_type=content_type, codename=codename
                        )
                        group.permissions.add(permission)
                        added_count += 1
                        self.stdout.write(
                            f"  ✓ {app_label}.{action}_{model_name}"
                        )
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠ Permission not found: {app_label}.{codename}"
                            )
                        )
            except ContentType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ ContentType not found: {app_label}.{model_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Admin Central group configured with {added_count} permissions"
            )
        )

        # Optionally assign users by role
        if assign_role:
            User = get_user_model()
            users = User.objects.filter(role__iexact=assign_role.strip())
            count = users.count()
            if count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠ No users found with role '{assign_role}'"
                    )
                )
            else:
                for user in users:
                    user.groups.add(group)
                    # Also ensure they have is_staff=True
                    if not user.is_staff:
                        user.is_staff = True
                        user.save(update_fields=["is_staff"])
                        self.stdout.write(
                            f"  ✓ Added {user.username} to group and set is_staff=True"
                        )
                    else:
                        self.stdout.write(
                            f"  ✓ Added {user.username} to group"
                        )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ {count} user(s) with role '{assign_role}' added to Admin Central group"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ Done! Users in 'Admin Central' group can now access /admin/ with full permissions."
            )
        )
