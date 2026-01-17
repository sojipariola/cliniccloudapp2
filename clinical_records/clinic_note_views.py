from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from common.tenant_scope import assign_tenant, enforce_tenant, scope_queryset
from patients.models import Patient
from tenants.models import Tenant

from .clinic_note_types import CLINIC_NOTE_TEMPLATES
from .models import ClinicalRecord


@login_required
def clinic_note_create(request):
    patients = scope_queryset(Patient.objects.all(), request.user)
    # Get specialization choices from Tenant model
    specialization_choices = Tenant.SPECIALIZATION_CHOICES
    # Default to tenant's specialization
    tenant_specialization = (
        request.user.tenant.specialization
        if request.user.tenant
        else "general_practice"
    )

    template = []
    values = {}
    patient_id = request.GET.get("patient") if request.method == "GET" else None
    note_type = None
    specialization = tenant_specialization

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        specialization = request.POST.get("specialization", tenant_specialization)
        note_type = request.POST.get("note_type")

        # Get template for this specialization
        available_notes = CLINIC_NOTE_TEMPLATES.get(
            specialization, CLINIC_NOTE_TEMPLATES.get("general_practice", [])
        )

        if note_type:
            # Build note content from form fields
            note_content = request.POST.get("note_content", "")

            if patient_id and note_content:
                ClinicalRecord.objects.create(
                    tenant=request.user.tenant
                    if not request.user.platform_admin
                    else patients.filter(pk=patient_id).first().tenant,
                    patient_id=patient_id,
                    note_type=note_type,
                    note=note_content,
                )
                return redirect("clinicalrecord_list")

        template = available_notes
    elif request.method == "GET":
        # Check if specialization is provided in URL
        specialization = request.GET.get("specialization", tenant_specialization)
        template = CLINIC_NOTE_TEMPLATES.get(
            specialization, CLINIC_NOTE_TEMPLATES.get("general_practice", [])
        )

    return render(
        request,
        "clinical_records/clinic_note_form.html",
        {
            "patients": patients,
            "specialization_choices": specialization_choices,
            "template": template,
            "values": values,
            "patient_id": patient_id,
            "note_type": note_type,
            "specialization": specialization,
            "tenant_specialization": tenant_specialization,
        },
    )
