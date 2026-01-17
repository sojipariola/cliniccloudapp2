import random
from django.core.management.base import BaseCommand
from patients.models import Patient


class Command(BaseCommand):
    help = 'Assign random genders to patients without gender information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Assign random genders to ALL patients (not just those without gender)',
        )
        parser.add_argument(
            '--male',
            type=int,
            default=None,
            help='Percentage of patients to assign as Male (0-100)',
        )
        parser.add_argument(
            '--female',
            type=int,
            default=None,
            help='Percentage of patients to assign as Female (0-100)',
        )

    def handle(self, *args, **options):
        if options['all']:
            patients = Patient.objects.all()
            self.stdout.write(
                self.style.WARNING(f'🔄 Assigning genders to ALL {patients.count()} patients...')
            )
        else:
            patients = Patient.objects.filter(gender__isnull=True)
            self.stdout.write(
                self.style.WARNING(f'🔄 Assigning genders to {patients.count()} patients without gender...')
            )

        if not patients.exists():
            self.stdout.write(self.style.SUCCESS('✅ All patients already have gender assigned!'))
            return

        # Default distribution
        male_percentage = options.get('male') or 50
        female_percentage = options.get('female') or 50
        other_percentage = max(0, 100 - male_percentage - female_percentage)

        updated_count = 0
        male_count = 0
        female_count = 0
        other_count = 0

        for patient in patients:
            rand = random.randint(0, 99)
            if rand < male_percentage:
                patient.gender = 'M'
                male_count += 1
            elif rand < male_percentage + female_percentage:
                patient.gender = 'F'
                female_count += 1
            else:
                patient.gender = 'O'
                other_count += 1
            
            patient.save()
            updated_count += 1
            self.stdout.write(
                f'  {updated_count}. {patient.first_name} {patient.last_name} → {patient.get_gender_display()}'
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully assigned genders!'))
        self.stdout.write(f'  Male: {male_count} ({male_count}/{updated_count})')
        self.stdout.write(f'  Female: {female_count} ({female_count}/{updated_count})')
        self.stdout.write(f'  Other: {other_count} ({other_count}/{updated_count})')
