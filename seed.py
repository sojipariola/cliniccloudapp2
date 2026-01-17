import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

import django
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from appointments.models import Appointment
from clinical_records.models import ClinicalRecord
from labs.models import LabResult
from patients.models import Patient
from referrals.models import Clinic, Referral
from documents.models import Document
from billing.models import PatientInvoice, InvoiceLineItem

# Import models after django.setup()
from tenants.models import Tenant
from users.models import CustomUser

# Clear existing data (optional - comment out if you want to keep existing data)
print("Clearing existing data...")
InvoiceLineItem.objects.all().delete()
PatientInvoice.objects.all().delete()
Document.objects.all().delete()
Referral.objects.all().delete()
Clinic.objects.all().delete()
ClinicalRecord.objects.all().delete()
LabResult.objects.all().delete()
Appointment.objects.all().delete()
Patient.objects.all().delete()
CustomUser.objects.all().delete()
Tenant.objects.all().delete()

# Sample clinical notes for different specializations
SAMPLE_NOTES = {
    "general_practice": [
        (
            "Chief Complaint",
            "Patient presents with persistent cough and mild fever for 3 days.",
        ),
        (
            "History of Present Illness",
            "38-year-old female with non-productive cough, low-grade fever (99.5°F), fatigue. No chest pain or shortness of breath.",
        ),
        ("Assessment", "Upper respiratory tract infection, likely viral etiology."),
        (
            "Plan",
            "Supportive care, rest, fluids. Return if symptoms worsen or persist beyond 7 days.",
        ),
    ],
    "pediatrics": [
        ("Chief Complaint", "6-month-old infant for routine well-child check."),
        (
            "Growth & Development",
            "Weight: 16 lbs (50th percentile). Length: 26 inches (60th percentile). Head circumference: 43 cm (55th percentile). Meeting developmental milestones.",
        ),
        (
            "Immunizations",
            "Administered DTaP, IPV, Hib, PCV13, and Rotavirus vaccines today.",
        ),
        ("Assessment", "Healthy infant, appropriate growth and development."),
        (
            "Plan",
            "Continue breastfeeding. Introduce solid foods. Next visit at 9 months.",
        ),
    ],
    "dental": [
        ("Dental Complaint", "Patient reports sensitivity in lower right molar."),
        (
            "Oral Exam",
            "Moderate plaque accumulation. Cavity noted on tooth #30 (lower right first molar). Gingival inflammation grade 2.",
        ),
        (
            "Radiographs",
            "Periapical x-ray shows decay extending to dentin, no pulpal involvement.",
        ),
        ("Assessment", "Dental caries tooth #30, gingivitis."),
        (
            "Treatment Plan",
            "Composite filling for tooth #30. Professional cleaning. Oral hygiene instruction.",
        ),
    ],
    "cardiology": [
        (
            "Cardiac Complaint",
            "65-year-old male with intermittent chest discomfort on exertion.",
        ),
        (
            "Cardiac History",
            "Hypertension x 10 years, controlled on lisinopril. Family history of CAD. Non-smoker.",
        ),
        (
            "Physical Exam",
            "BP 138/82, HR 76 regular. Heart sounds normal, no murmurs. Lungs clear.",
        ),
        ("ECG/Echo", "ECG shows normal sinus rhythm, no ST changes. Echo pending."),
        ("Assessment", "Stable angina, likely coronary artery disease."),
        (
            "Plan",
            "Stress test scheduled. Start aspirin 81mg daily. Optimize BP control. Lipid panel.",
        ),
    ],
    "dermatology": [
        (
            "Skin Complaint",
            "New pigmented lesion on back, changing appearance over 2 months.",
        ),
        (
            "Dermatologic History",
            "Fair skin, multiple sunburns in childhood. No family history of melanoma.",
        ),
        (
            "Skin Exam",
            "8mm asymmetric, irregular bordered pigmented lesion left scapular region. Multiple benign nevi elsewhere.",
        ),
        ("Assessment", "Suspicious pigmented lesion, rule out melanoma."),
        (
            "Plan",
            "Excisional biopsy with 2mm margins scheduled. Dermoscopy performed. Full body skin exam in 6 months.",
        ),
    ],
    "mental_health": [
        (
            "Presenting Problem",
            "32-year-old patient with persistent low mood and anxiety for 6 weeks.",
        ),
        (
            "Psychiatric History",
            "First episode. No prior psychiatric treatment. No suicidal ideation. Family history of depression.",
        ),
        (
            "Mental Status Exam",
            "Appears anxious, good eye contact. Speech normal rate. Mood depressed, affect congruent. Thought process linear. No SI/HI.",
        ),
        (
            "Assessment",
            "Major depressive disorder, moderate severity. Generalized anxiety disorder.",
        ),
        (
            "Plan",
            "Start sertraline 50mg daily. Cognitive behavioral therapy referral. Follow-up in 2 weeks.",
        ),
    ],
    "orthopedic": [
        (
            "Musculoskeletal Complaint",
            "42-year-old male with right knee pain after twisting injury while playing basketball.",
        ),
        (
            "Ortho History",
            "Acute onset 3 days ago. Pain with weight-bearing and twisting. Swelling noted. No prior knee injuries.",
        ),
        (
            "Physical Exam",
            "Right knee: moderate effusion, joint line tenderness, positive McMurray test, stable ligaments.",
        ),
        ("Imaging", "X-ray: no fracture. MRI ordered to evaluate meniscus."),
        ("Assessment", "Suspected medial meniscus tear, right knee."),
        (
            "Plan",
            "RICE protocol. NSAIDs. Crutches. Await MRI. Consider arthroscopy if torn.",
        ),
    ],
}

# Tenants with different specializations
print("Creating tenants...")
tenant1 = Tenant.objects.create(
    name="Central Medical Clinic",
    subdomain="central",
    specialization="general_practice",
    plan="professional",
)
tenant2 = Tenant.objects.create(
    name="Children's Health Pediatrics",
    subdomain="childrens",
    specialization="pediatrics",
    plan="professional",
)
tenant3 = Tenant.objects.create(
    name="Bright Smile Dental",
    subdomain="brightsmile",
    specialization="dental",
    plan="starter",
)
tenant4 = Tenant.objects.create(
    name="HeartCare Cardiology",
    subdomain="heartcare",
    specialization="cardiology",
    plan="professional",
)
tenant5 = Tenant.objects.create(
    name="SkinHealth Dermatology",
    subdomain="skinhealth",
    specialization="dermatology",
    plan="professional",
)
tenant6 = Tenant.objects.create(
    name="MindWell Mental Health",
    subdomain="mindwell",
    specialization="mental_health",
    plan="starter",
)
tenant7 = Tenant.objects.create(
    name="OrthoSport Clinic",
    subdomain="orthosport",
    specialization="orthopedic",
    plan="professional",
)

tenants = [tenant1, tenant2, tenant3, tenant4, tenant5, tenant6, tenant7]

# Users for each tenant
print("Creating users...")
users = []
for idx, tenant in enumerate(tenants, 1):
    admin = CustomUser.objects.create(
        username=f"admin{idx}",
        email=f"admin{idx}@{tenant.subdomain}.com",
        first_name=f"Admin",
        last_name=f"{tenant.name.split()[0]}",
        tenant=tenant,
        role="admin",
        is_staff=True,
        is_active=True,
        password=make_password("admin123"),
    )
    users.append(admin)

    # Add a regular user for each tenant
    user = CustomUser.objects.create(
        username=f"doctor{idx}",
        email=f"doctor{idx}@{tenant.subdomain}.com",
        first_name=f"Doctor",
        last_name=f"{tenant.name.split()[0]}",
        tenant=tenant,
        role="user",
        is_active=True,
        password=make_password("doctor123"),
    )
    users.append(user)

# Sample patient names
first_names = [
    "James",
    "Mary",
    "John",
    "Patricia",
    "Robert",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Charles",
    "Karen",
]
last_names = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
]

# Patients for each tenant
print("Creating patients...")
all_patients = []
for tenant in tenants:
    tenant_patients = []
    for i in range(10):  # 10 patients per tenant
        patient = Patient.objects.create(
            tenant=tenant,
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            date_of_birth=(
                datetime.now() - timedelta(days=random.randint(365 * 5, 365 * 80))
            ).date(),
            email=f"patient{len(all_patients)+1}@example.com",
            phone=f"555-{random.randint(1000, 9999)}",
        )
        tenant_patients.append(patient)
        all_patients.append(patient)

    # Create clinical notes for patients
    print(f"Creating clinical notes for {tenant.name}...")
    note_templates = SAMPLE_NOTES.get(
        tenant.specialization, SAMPLE_NOTES["general_practice"]
    )

    for patient in tenant_patients[:7]:  # Add notes for first 7 patients
        # Randomly select number of notes (1-3 per patient)
        num_notes = random.randint(1, 3)
        for _ in range(num_notes):
            note_type = random.choice([template[0] for template in note_templates])
            # Build note content from template
            note_content = "\n\n".join(
                [f"{section}:\n{content}" for section, content in note_templates]
            )

            ClinicalRecord.objects.create(
                tenant=tenant,
                patient=patient,
                note_type=note_type,
                note=note_content,
                created_at=datetime.now() - timedelta(days=random.randint(1, 180)),
            )

    # Create appointments
    print(f"Creating appointments for {tenant.name}...")
    for patient in tenant_patients[:8]:  # Appointments for first 8 patients
        # Create 1-2 appointments per patient
        for j in range(random.randint(1, 2)):
            days_offset = random.randint(-30, 60)  # Past or future appointments
            status = (
                random.choice(["scheduled", "completed", "cancelled"])
                if days_offset < 0
                else "scheduled"
            )

            Appointment.objects.create(
                tenant=tenant,
                patient=patient,
                scheduled_for=datetime.now() + timedelta(days=days_offset),
                status=status,
            )

    # Create lab results
    print(f"Creating lab results for {tenant.name}...")
    for patient in tenant_patients[:6]:  # Lab results for first 6 patients
        lab_types = [
            "Complete Blood Count",
            "Metabolic Panel",
            "Lipid Panel",
            "Urinalysis",
            "HbA1c",
        ]
        result_texts = [
            "WBC: 7.2 K/uL, RBC: 4.8 M/uL, Hemoglobin: 14.5 g/dL, Platelets: 250 K/uL - All values within normal limits.",
            "Glucose: 92 mg/dL, BUN: 15 mg/dL, Creatinine: 0.9 mg/dL, Sodium: 140 mEq/L, Potassium: 4.2 mEq/L - Normal.",
            "Total Cholesterol: 185 mg/dL, LDL: 110 mg/dL, HDL: 55 mg/dL, Triglycerides: 100 mg/dL - Optimal levels.",
            "Color: Yellow, Clarity: Clear, pH: 6.5, Glucose: Negative, Protein: Negative - Normal urinalysis.",
            "HbA1c: 5.6% - Normal glucose control, no evidence of diabetes.",
        ]

        lab_result = random.choice(list(zip(lab_types, result_texts)))
        LabResult.objects.create(
            tenant=tenant,
            patient=patient,
            result=f"{lab_result[0]}:\n{lab_result[1]}",
            created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
        )

print("\n" + "=" * 60)
print("Creating clinics for referrals...")
print("=" * 60)
# Create clinics for each tenant
all_clinics = []
clinic_types = ["cardiology", "dermatology", "orthopedic", "neurology", "ent", "urology", "gastroenterology"]
for tenant in tenants:
    # Create 3-5 clinics per tenant
    for _ in range(random.randint(3, 5)):
        clinic = Clinic.objects.create(
            tenant=tenant,
            name=f"{random.choice(['Central', 'City', 'Regional', 'Community', 'Specialist'])} {random.choice(clinic_types).title()} Clinic",
            clinic_type=random.choice(clinic_types)
        )
        all_clinics.append(clinic)

print(f"Created {len(all_clinics)} clinics")

print("\n" + "=" * 60)
print("Creating referrals for patients...")
print("=" * 60)
# Create referrals for patients
for tenant in tenants:
    tenant_patients = [p for p in all_patients if p.tenant == tenant]
    tenant_clinics = [c for c in all_clinics if c.tenant == tenant]
    tenant_users = [u for u in users if u.tenant == tenant]
    
    if len(tenant_clinics) >= 2:
        for patient in tenant_patients[:6]:  # Referrals for first 6 patients
            # Create 1-2 referrals per patient
            for _ in range(random.randint(1, 2)):
                from_clinic = random.choice(tenant_clinics)
                to_clinic = random.choice([c for c in tenant_clinics if c != from_clinic])
                
                referral_notes = [
                    "Patient requires specialist consultation for ongoing symptoms.",
                    "Follow-up recommended for advanced diagnostic evaluation.",
                    "Referral for additional treatment options and specialist opinion.",
                    "Patient presents with complex case requiring specialized care.",
                    "Consultation requested for treatment plan optimization."
                ]
                
                Referral.objects.create(
                    tenant=tenant,
                    patient=patient,
                    from_clinic=from_clinic,
                    to_clinic=to_clinic,
                    referred_by=random.choice(tenant_users),
                    notes=random.choice(referral_notes),
                    accepted=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )

print(f"Created {Referral.objects.count()} referrals")

print("\n" + "=" * 60)
print("Creating documents for patients...")
print("=" * 60)
# Create sample documents for patients
document_types = [
    ("Lab Report - Blood Test Results", "lab_report_bloodwork.pdf"),
    ("X-Ray Imaging Report", "xray_chest_2024.pdf"),
    ("MRI Scan Results", "mri_brain_scan.pdf"),
    ("Prescription Record", "prescription_2024_01.pdf"),
    ("Vaccination Certificate", "vaccination_covid19.pdf"),
    ("Consultation Notes", "consultation_summary.pdf"),
    ("Insurance Form", "insurance_claim_form.pdf"),
]

for tenant in tenants:
    tenant_patients = [p for p in all_patients if p.tenant == tenant]
    tenant_users = [u for u in users if u.tenant == tenant]
    
    for patient in tenant_patients[:7]:  # Documents for first 7 patients
        # Create 1-3 documents per patient
        for _ in range(random.randint(1, 3)):
            doc_type = random.choice(document_types)
            # Create a dummy file
            dummy_content = f"Sample document content for {patient.first_name} {patient.last_name}\nDocument Type: {doc_type[0]}\nGenerated: {datetime.now()}"
            
            doc = Document.objects.create(
                patient=patient,
                uploaded_by=random.choice(tenant_users),
                description=doc_type[0],
                uploaded_at=datetime.now() - timedelta(days=random.randint(1, 90))
            )
            # Save dummy file
            doc.file.save(doc_type[1], ContentFile(dummy_content.encode()), save=True)

print(f"Created {Document.objects.count()} documents")

print("\n" + "=" * 60)
print("Creating patient invoices...")
print("=" * 60)
# Create patient invoices
invoice_services = [
    ("General Consultation", "consultation", Decimal("75.00")),
    ("Follow-up Visit", "consultation", Decimal("50.00")),
    ("Blood Test Panel", "test", Decimal("120.00")),
    ("X-Ray Imaging", "imaging", Decimal("150.00")),
    ("MRI Scan", "imaging", Decimal("450.00")),
    ("Minor Procedure", "procedure", Decimal("200.00")),
    ("Vaccination", "medication", Decimal("35.00")),
    ("Physical Therapy Session", "procedure", Decimal("85.00")),
]

invoice_counter = 1000
for tenant in tenants:
    tenant_patients = [p for p in all_patients if p.tenant == tenant]
    
    for patient in tenant_patients[:8]:  # Invoices for first 8 patients
        # Create 1-3 invoices per patient
        for _ in range(random.randint(1, 3)):
            invoice_counter += 1
            days_ago = random.randint(1, 120)
            issue_date = (datetime.now() - timedelta(days=days_ago)).date()
            due_date = issue_date + timedelta(days=30)
            
            status = random.choice(["sent", "paid", "overdue", "paid", "sent"])  # More likely to be paid or sent
            paid_date = None
            if status == "paid":
                paid_date = issue_date + timedelta(days=random.randint(1, 25))
            
            invoice = PatientInvoice.objects.create(
                tenant=tenant,
                patient=patient,
                invoice_number=f"INV-{invoice_counter}",
                status=status,
                issued_date=issue_date,
                due_date=due_date,
                paid_date=paid_date,
                tax=Decimal("0.00"),
                currency="GBP"
            )
            
            # Add 1-4 line items per invoice
            for _ in range(random.randint(1, 4)):
                service = random.choice(invoice_services)
                quantity = random.randint(1, 3)
                
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=service[0],
                    service_type=service[1],
                    quantity=Decimal(str(quantity)),
                    unit_price=service[2],
                    total=Decimal(str(quantity)) * service[2]
                )
            
            # Calculate invoice total
            invoice.calculate_total()
            invoice.save()

print(f"Created {PatientInvoice.objects.count()} invoices with {InvoiceLineItem.objects.count()} line items")

print("\n" + "=" * 60)
print("Database seeded successfully!")
print("=" * 60)
print(f"\nCreated:")
print(f"  - {Tenant.objects.count()} tenants")
print(f"  - {CustomUser.objects.count()} users")
print(f"  - {Patient.objects.count()} patients")
print(f"  - {ClinicalRecord.objects.count()} clinical records")
print(f"  - {Appointment.objects.count()} appointments")
print(f"  - {LabResult.objects.count()} lab results")
print(f"  - {Clinic.objects.count()} clinics")
print(f"  - {Referral.objects.count()} referrals")
print(f"  - {Document.objects.count()} documents")
print(f"  - {PatientInvoice.objects.count()} patient invoices")
print(f"  - {InvoiceLineItem.objects.count()} invoice line items")
print("\nLogin credentials:")
print("  Admin users: admin1-admin7 / admin123")
print("  Doctor users: doctor1-doctor7 / doctor123")
print("\nTenants and specializations:")
for tenant in Tenant.objects.all():
    print(
        f"  - {tenant.name}: {tenant.get_specialization_display()} ({tenant.subdomain}.localhost)"
    )
print("=" * 60)
