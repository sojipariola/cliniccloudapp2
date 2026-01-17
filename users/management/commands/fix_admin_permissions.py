from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Fix admin user permissions for Django admin access'

    def handle(self, *args, **options):
        # Get all staff users and make them superusers
        admin_users = CustomUser.objects.filter(is_staff=True)
        
        if not admin_users.exists():
            self.stdout.write(
                self.style.ERROR('❌ No staff users found. Please create an admin user first.')
            )
            return
        
        updated = 0
        for user in admin_users:
            if not user.is_superuser:
                user.is_superuser = True
                user.is_active = True
                user.platform_admin = True
                user.save()
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Fixed permissions for "{user.username}"')
                )
        
        if updated == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  All admin users already have superuser permissions.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {updated} admin user(s) permissions fixed!')
            )
