import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from tenants.models import Tenant
from patients.models import Patient
from referrals.models import Clinic
from clinical_records.models import ClinicalRecord


class Command(BaseCommand):
    help = 'Setup Central Medical Clinic: move patients, create 25 specialties, seed clinical records'

    # 25 Medical Specialties
    SPECIALTIES = [
        'Cardiology',
        'Dermatology',
        'Neurology',
        'Orthopedic Surgery',
        'General Surgery',
        'Internal Medicine',
        'Pediatrics',
        'Psychiatry',
        'Ophthalmology',
        'Otolaryngology',
        'Urology',
        'Gynecology',
        'Gastroenterology',
        'Pulmonology',
        'Rheumatology',
        'Endocrinology',
        'Nephrology',
        'Hematology',
        'Oncology',
        'Radiology',
        'Pathology',
        'Anesthesiology',
        'Emergency Medicine',
        'Family Medicine',
        'Physical Medicine & Rehabilitation',
    ]

    # Clinical note types for each specialty
    SPECIALTY_NOTES = {
        'Cardiology': [
            'Cardiac History',
            'ECG/Echo',
            'Cardiac Complaint',
            'Chest Pain Assessment',
            'Arrhythmia Evaluation',
        ],
        'Dermatology': [
            'Skin Complaint',
            'Dermatologic History',
            'Skin Assessment',
            'Lesion Evaluation',
            'Allergy Assessment',
        ],
        'Neurology': [
            'Neurological History',
            'Neuro Exam',
            'Headache Assessment',
            'Seizure Evaluation',
            'Cognitive Assessment',
        ],
        'Orthopedic Surgery': [
            'Ortho History',
            'Joint Assessment',
            'Injury Evaluation',
            'Fracture Assessment',
            'Mobility Evaluation',
        ],
        'General Surgery': [
            'Surgical History',
            'Abdomen Assessment',
            'Surgical Complaint',
            'Wound Assessment',
            'Pre-operative Evaluation',
        ],
        'Internal Medicine': [
            'Chief Complaint',
            'History of Present Illness',
            'Physical Exam',
            'Assessment',
            'Plan',
        ],
        'Pediatrics': [
            'Growth & Development',
            'Immunizations',
            'Pediatric History',
            'Feeding Assessment',
            'Developmental Milestone',
        ],
        'Psychiatry': [
            'Psychiatric History',
            'Mental Status Exam',
            'Mood Assessment',
            'Anxiety Evaluation',
            'Substance Use History',
        ],
        'Ophthalmology': [
            'Eye Complaint',
            'Vision Assessment',
            'Eye Exam',
            'Visual Acuity',
            'Ocular History',
        ],
        'Otolaryngology': [
            'ENT Complaint',
            'Ear Assessment',
            'Throat Assessment',
            'Hearing Evaluation',
            'ENT History',
        ],
        'Urology': [
            'Urological History',
            'Urinary Complaint',
            'Prostate Assessment',
            'Renal Function',
            'Urological Exam',
        ],
        'Gynecology': [
            'Gynecological History',
            'Reproductive Assessment',
            'Pregnancy Assessment',
            'Menstrual History',
            'Gynecological Exam',
        ],
        'Gastroenterology': [
            'GI History',
            'Abdominal Complaint',
            'Bowel Assessment',
            'Digestive Assessment',
            'GI Exam',
        ],
        'Pulmonology': [
            'Respiratory History',
            'Lung Assessment',
            'Cough Evaluation',
            'Breathing Assessment',
            'Pulmonary Function',
        ],
        'Rheumatology': [
            'Rheumatologic History',
            'Joint Assessment',
            'Autoimmune Screening',
            'Inflammation Assessment',
            'Rheumatologic Exam',
        ],
        'Endocrinology': [
            'Endocrine History',
            'Metabolic Assessment',
            'Glucose Assessment',
            'Thyroid Evaluation',
            'Hormone Assessment',
        ],
        'Nephrology': [
            'Renal History',
            'Kidney Function',
            'Fluid Balance Assessment',
            'Renal Exam',
            'Electrolyte Assessment',
        ],
        'Hematology': [
            'Hematologic History',
            'Blood Assessment',
            'Anemia Evaluation',
            'Clotting Assessment',
            'Lab Analysis',
        ],
        'Oncology': [
            'Cancer History',
            'Tumor Assessment',
            'Cancer Staging',
            'Treatment Planning',
            'Follow-up Assessment',
        ],
        'Radiology': [
            'Imaging Request',
            'Radiological Report',
            'Image Interpretation',
            'Scan Results',
            'Diagnostic Imaging',
        ],
        'Pathology': [
            'Specimen Analysis',
            'Pathology Report',
            'Tissue Assessment',
            'Lab Finding',
            'Diagnostic Pathology',
        ],
        'Anesthesiology': [
            'Anesthesia History',
            'Pre-operative Assessment',
            'Anesthetic Plan',
            'Recovery Assessment',
            'Pain Assessment',
        ],
        'Emergency Medicine': [
            'Emergency Complaint',
            'Acute Assessment',
            'Trauma Assessment',
            'Critical Assessment',
            'Emergency Plan',
        ],
        'Family Medicine': [
            'Chief Complaint',
            'History of Present Illness',
            'Physical Exam',
            'Assessment',
            'Plan',
        ],
        'Physical Medicine & Rehabilitation': [
            'Rehabilitation History',
            'Functional Assessment',
            'Physical Therapy Plan',
            'Rehabilitation Progress',
            'Mobility Assessment',
        ],
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Starting Central Medical Clinic Setup...\n'))

        # Step 1: Get or create Central Medical Clinic tenant
        central, created = Tenant.objects.get_or_create(
            name='Central Medical Clinic',
            defaults={'specialization': 'general_practice', 'is_active': True}
        )
        self.stdout.write(f'✅ Central Medical Clinic: {central.name} (ID: {central.id})')

        # Step 2: Move all patients to Central Medical Clinic
        self.stdout.write(self.style.WARNING(f'\n📋 Moving all patients to Central Medical Clinic...'))
        all_patients = Patient.objects.all()
        count = 0
        for patient in all_patients:
            patient.tenant = central
            patient.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ Moved {count} patients to Central Medical Clinic'))

        # Step 3: Delete existing clinics and create 25 specialties
        self.stdout.write(self.style.WARNING(f'\n🏥 Creating 25 clinical specialties...'))
        Clinic.objects.filter(tenant=central).delete()
        
        created_clinics = []
        clinic_type_map = {
            'Cardiology': 'cardiology',
            'Dermatology': 'dermatology',
            'Neurology': 'neurology',
            'Orthopedic Surgery': 'orthopedic',
            'General Surgery': 'surgical',
            'Internal Medicine': 'general_practice',
            'Pediatrics': 'pediatrics',
            'Psychiatry': 'mental_health',
            'Ophthalmology': 'eye',
            'Otolaryngology': 'ent',
            'Urology': 'urology',
            'Gynecology': 'womens_health',
            'Gastroenterology': 'gastroenterology',
            'Pulmonology': 'surgical',
            'Rheumatology': 'allergy',
            'Endocrinology': 'endocrinology',
            'Nephrology': 'surgical',
            'Hematology': 'oncology',
            'Oncology': 'oncology',
            'Radiology': 'surgical',
            'Pathology': 'surgical',
            'Anesthesiology': 'surgical',
            'Emergency Medicine': 'urgent_care',
            'Family Medicine': 'general_practice',
            'Physical Medicine & Rehabilitation': 'physiotherapy',
        }
        
        for i, specialty in enumerate(self.SPECIALTIES, 1):
            clinic_type = clinic_type_map.get(specialty, 'general_practice')
            clinic = Clinic.objects.create(
                tenant=central,
                name=f'{specialty} Department',
                clinic_type=clinic_type,
            )
            created_clinics.append(clinic)
            self.stdout.write(f'  {i:2}. {clinic.name}')

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(created_clinics)} clinics'))

        # Step 4: Seed clinical records for all specialties
        self.stdout.write(self.style.WARNING(f'\n📝 Seeding clinical records for all specialties...'))
        
        central_patients = Patient.objects.filter(tenant=central)
        if not central_patients.exists():
            self.stdout.write(self.style.ERROR('❌ No patients found!'))
            return

        total_records_created = 0
        
        for clinic in created_clinics:
            specialty = clinic.clinic_type.replace('_', ' ').title()
            note_types = self.SPECIALTY_NOTES.get(clinic.name.replace(' Department', ''), [])
            
            if not note_types:
                note_types = ['Chief Complaint', 'History of Present Illness', 'Physical Exam', 'Assessment', 'Plan']
            
            # Create 3-5 clinical records per specialty
            records_per_specialty = random.randint(3, 5)
            
            for j in range(records_per_specialty):
                patient = random.choice(central_patients)
                note_type = random.choice(note_types)
                
                record = ClinicalRecord.objects.create(
                    patient=patient,
                    tenant=central,
                    note_type=note_type,
                    chief_complaint=f'{specialty} consultation - {note_type}',
                    history_of_present_illness=f'Patient presenting with {specialty}-related symptoms requiring {note_type} assessment.',
                    past_medical_history='See patient records for complete medical history.',
                    medications_history='Current medications per pharmacy records.',
                    allergy_history='No known drug allergies.',
                    physical_exam_inspection='General appearance appropriate for age.',
                    physical_exam_palpation='Palpation performed with no acute tenderness.',
                    physical_exam_percussion='Percussion findings within normal limits.',
                    physical_exam_auscultation='Auscultation reveals normal findings.',
                    provisional_diagnosis=f'Suspected {specialty} condition requiring further evaluation.',
                    investigations_ordered=f'Relevant tests and imaging for {specialty} assessment ordered.',
                    investigation_results='Pending investigation results.',
                    assessment_diagnosis=f'{specialty} assessment complete.',
                    plan=f'Continue monitoring. Follow-up in {specialty} clinic in 2 weeks.',
                    note=f'Comprehensive {specialty} clinical note created for documentation.',
                )
                
                total_records_created += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {total_records_created} clinical records'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ CENTRAL MEDICAL CLINIC SETUP COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Patients: {central_patients.count()}')
        self.stdout.write(f'  Specialties: {len(created_clinics)}')
        self.stdout.write(f'  Clinical Records: {total_records_created}')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
