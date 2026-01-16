"""
Management command to create a superuser with tenant assignment.
This is needed because the CustomUser model requires a tenant_id.

Usage:
  python manage.py createsuperuser_tenant --username admin --email admin@example.com --tenant-name DefaultTenant
  or interactively:
  python manage.py createsuperuser_tenant
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from tenants.models import Tenant
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with tenant assignment (required for multi-tenant CustomUser model)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Username for the superuser',
        )
        parser.add_argument(
            '--email',
            help='Email address for the superuser',
        )
        parser.add_argument(
            '--tenant-name',
            help='Tenant name (will create if not exists)',
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='Tenant ID (optional, will use name if provided)',
        )
        parser.add_argument(
            '--password',
            help='Password for the superuser (will prompt if not provided)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating multi-tenant superuser...'))
        
        # Get or create tenant
        if options.get('tenant_id'):
            try:
                tenant = Tenant.objects.get(id=options['tenant_id'])
                self.stdout.write(f"✓ Using existing tenant: {tenant.name} (ID: {tenant.id})")
            except Tenant.DoesNotExist:
                raise CommandError(f"Tenant with ID {options['tenant_id']} does not exist")
        elif options.get('tenant_name'):
            tenant_name = options['tenant_name']
            tenant, created = Tenant.objects.get_or_create(
                name=tenant_name,
                defaults={
                    'subdomain': tenant_name.lower().replace(' ', '-'),
                    'plan': 'free_trial',
                    'trial_started_at': timezone.now(),
                    'trial_ended_at': timezone.now() + timedelta(days=14),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created tenant: {tenant.name} (ID: {tenant.id})"))
            else:
                self.stdout.write(f"✓ Using existing tenant: {tenant.name} (ID: {tenant.id})")
        else:
            # Interactive mode - list tenants
            existing_tenants = list(Tenant.objects.all())
            if existing_tenants:
                self.stdout.write("\nExisting tenants:")
                for t in existing_tenants:
                    self.stdout.write(f"  {t.id}: {t.name} ({t.subdomain})")
                
                tenant_id = input("\nEnter tenant ID (or 'new' to create new): ").strip()
                
                if tenant_id.lower() == 'new':
                    tenant_name = input("Enter new tenant name: ").strip()
                    tenant, _ = Tenant.objects.get_or_create(
                        name=tenant_name,
                        defaults={
                            'subdomain': tenant_name.lower().replace(' ', '-'),
                            'plan': 'free_trial',
                            'trial_started_at': timezone.now(),
                            'trial_ended_at': timezone.now() + timedelta(days=14),
                            'is_active': True,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"✓ Created tenant: {tenant.name}"))
                else:
                    try:
                        tenant = Tenant.objects.get(id=int(tenant_id))
                        self.stdout.write(f"✓ Using tenant: {tenant.name}")
                    except (Tenant.DoesNotExist, ValueError):
                        raise CommandError(f"Invalid tenant ID: {tenant_id}")
            else:
                # No tenants exist, create default
                tenant, _ = Tenant.objects.get_or_create(
                    name='DefaultTenant',
                    defaults={
                        'subdomain': 'default',
                        'plan': 'free_trial',
                        'trial_started_at': timezone.now(),
                        'trial_ended_at': timezone.now() + timedelta(days=14),
                        'is_active': True,
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Created default tenant: {tenant.name}"))

        # Get superuser details
        username = options.get('username') or input('Username: ').strip()
        email = options.get('email') or input('Email address: ').strip()
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f"User with username '{username}' already exists")
        
        # Get password
        password = options.get('password')
        if not password:
            from getpass import getpass
            while True:
                password1 = getpass('Password: ')
                password2 = getpass('Password (again): ')
                if password1 == password2:
                    password = password1
                    break
                else:
                    self.stdout.write(self.style.ERROR('Passwords do not match. Try again.'))
        
        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                tenant=tenant,
            )
            user.platform_admin = True
            user.save()
            
            self.stdout.write(self.style.SUCCESS('\n✓ Successfully created superuser:'))
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Tenant: {user.tenant.name}')
            self.stdout.write('  Platform Admin: True')
            self.stdout.write('\nYou can now login at: /admin/')
        except Exception as e:
            raise CommandError(f'Failed to create superuser: {str(e)}')
