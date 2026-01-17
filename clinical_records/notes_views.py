from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from common.tenant_scope import scope_queryset
from clinical_records.models import ClinicalRecord
from patients.models import Patient


@login_required
def notes_dashboard(request):
    """View all notes for patients - hub for both AI and Clinic-specific notes."""
    patient_id = request.GET.get('patient')
    patient = None
    notes = []
    
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
        notes = scope_queryset(
            ClinicalRecord.objects.filter(patient=patient),
            request.user
        ).order_by('-created_at')
    else:
        # Show recent notes for all accessible patients
        notes = scope_queryset(
            ClinicalRecord.objects.all(),
            request.user
        ).order_by('-created_at')[:20]
    
    return render(request, 'clinical_records/notes_dashboard.html', {
        'notes': notes,
        'patient': patient,
    })
