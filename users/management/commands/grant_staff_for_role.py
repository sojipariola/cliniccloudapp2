from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Grant Django admin access (is_staff=True) to users by role. "
        "Optionally scope by tenant or username."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--role",
            required=True,
            help="Role name to match (case-insensitive, e.g., 'Admin Central')",
        )
        parser.add_argument(
            "--tenant-id",
            type=int,
            help="Optional tenant ID to scope the update",
        )
        parser.add_argument(
            "--username",
            help="Optional specific username to update (overrides role filter if provided)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        role = options["role"].strip()
        tenant_id = options.get("tenant_id")
        username = options.get("username")
        dry_run = options.get("dry_run", False)

        qs = User.objects.all()
        if username:
            qs = qs.filter(username=username)
        else:
            qs = qs.filter(role__iexact=role)
            if tenant_id:
                qs = qs.filter(tenant_id=tenant_id)

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No matching users found."))
            return

        self.stdout.write(f"Found {count} user(s) to update.")
        updated = 0
        for user in qs:
            if not user.is_staff:
                if dry_run:
                    self.stdout.write(
                        f"DRY RUN: would set is_staff=True for {user.username} (tenant={user.tenant_id}, role={user.role})"
                    )
                else:
                    user.is_staff = True
                    user.save(update_fields=["is_staff"])
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated {user.username}: is_staff=True (tenant={user.tenant_id}, role={user.role})"
                        )
                    )
            else:
                self.stdout.write(
                    f"Skipping {user.username}: already is_staff=True (tenant={user.tenant_id}, role={user.role})"
                )

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f"Done. {updated} user(s) updated."))
