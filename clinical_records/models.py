from django.db import models

from patients.models import Patient
from tenants.models import Tenant


class ClinicalRecord(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="clinical_records"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="clinical_records"
    )
    note_type = models.CharField(
        max_length=50,
        default="general",
        help_text="Type of clinical note based on specialization",
    )
    note = models.TextField(blank=True)
    
    # SOAP Note Sections
    chief_complaint = models.TextField(blank=True, null=True)
    history_of_present_illness = models.TextField(blank=True, null=True)
    past_medical_history = models.TextField(blank=True, null=True)
    medications_history = models.TextField(blank=True, null=True)
    allergy_history = models.TextField(blank=True, null=True)
    
    # Physical Examination (4 components of physical exam)
    physical_exam_inspection = models.TextField(blank=True, null=True)
    physical_exam_palpation = models.TextField(blank=True, null=True)
    physical_exam_percussion = models.TextField(blank=True, null=True)
    physical_exam_auscultation = models.TextField(blank=True, null=True)
    
    # Assessment and Plan
    provisional_diagnosis = models.TextField(blank=True, null=True)
    investigations_ordered = models.TextField(blank=True, null=True)
    investigation_results = models.TextField(blank=True, null=True)
    assessment_diagnosis = models.TextField(blank=True, null=True)
    plan = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record for {self.patient} at {self.created_at}"
