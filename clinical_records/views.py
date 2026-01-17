from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from common.tenant_scope import assign_tenant, enforce_tenant, scope_queryset
from patients.models import Patient

from .forms import ClinicalRecordForm
from .models import ClinicalRecord


def get_changed_fields(old_instance, form_data):
    """
    Compare old instance with form data and return list of changed fields.
    Returns a dict with field name and (old_value, new_value) tuples.
    """
    changed = {}
    soap_fields = [
        "chief_complaint",
        "history_of_present_illness",
        "past_medical_history",
        "medications_history",
        "allergy_history",
        "physical_exam_inspection",
        "physical_exam_palpation",
        "physical_exam_percussion",
        "physical_exam_auscultation",
        "provisional_diagnosis",
        "investigations_ordered",
        "investigation_results",
        "assessment_diagnosis",
        "plan",
        "note_type",
        "note",
    ]
    
    for field in soap_fields:
        old_value = getattr(old_instance, field, "")
        new_value = form_data.get(field, "")
        
        # Normalize empty values
        old_value = old_value.strip() if old_value else ""
        new_value = new_value.strip() if new_value else ""
        
        if old_value != new_value:
            changed[field] = {
                "old": old_value[:100],  # Truncate for display
                "new": new_value[:100],
                "label": field.replace("_", " ").title(),
            }
    
    return changed


@login_required
@permission_required("clinical_records.change_clinicalrecord", raise_exception=True)
def clinicalrecord_edit(request, pk):
    record = enforce_tenant(get_object_or_404(ClinicalRecord, pk=pk), request.user)
    
    if request.method == "POST":
        # Check if this is a confirmation submission
        if request.POST.get("confirm_changes") == "true":
            form = ClinicalRecordForm(request.POST, instance=record, request=request)
            if form.is_valid():
                form.save()
                return redirect(reverse("clinicalrecord_detail", args=[record.pk]))
        else:
            # First submission - show changes
            form = ClinicalRecordForm(request.POST, instance=record, request=request)
            if form.is_valid():
                # Get changed fields
                changed_fields = get_changed_fields(record, request.POST)
                
                if changed_fields:
                    # Return the form with changes highlighted for confirmation
                    context = {
                        "form": form,
                        "edit": True,
                        "changes": changed_fields,
                        "show_confirmation": True,
                        "specialization": request.user.tenant.get_specialization_display()
                        if request.user.tenant
                        else "General Practice",
                    }
                    return render(request, "clinical_records/clinicalrecord_form.html", context)
                else:
                    # No changes, just save
                    form.save()
                    return redirect(reverse("clinicalrecord_detail", args=[record.pk]))
    else:
        form = ClinicalRecordForm(instance=record, request=request)
    
    context = {
        "form": form,
        "edit": True,
        "specialization": request.user.tenant.get_specialization_display()
        if request.user.tenant
        else "General Practice",
    }
    return render(request, "clinical_records/clinicalrecord_form.html", context)


@login_required
@permission_required("clinical_records.delete_clinicalrecord", raise_exception=True)
def clinicalrecord_archive(request, pk):
    record = enforce_tenant(get_object_or_404(ClinicalRecord, pk=pk), request.user)
    if request.method == "POST":
        record.note = "[ARCHIVED] " + record.note
        record.save()
        return redirect(reverse("clinicalrecord_list"))
    return render(
        request,
        "clinical_records/clinicalrecord_confirm_archive.html",
        {"record": record},
    )


@login_required
def clinicalrecord_list(request):
    records = scope_queryset(
        ClinicalRecord.objects.select_related("patient"), request.user
    ).order_by("-created_at")
    
    # Pagination
    paginator = Paginator(records, 10)  # 10 records per page
    page = request.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)
    
    return render(
        request, "clinical_records/clinicalrecord_list.html", {"records": records}
    )


@login_required
def clinicalrecord_detail(request, pk):
    record = enforce_tenant(get_object_or_404(ClinicalRecord, pk=pk), request.user)
    return render(
        request, "clinical_records/clinicalrecord_detail.html", {"record": record}
    )


@login_required
def clinicalrecord_create(request):
    if request.method == "POST":
        form = ClinicalRecordForm(request.POST, request=request)
        if form.is_valid():
            record = assign_tenant(form.save(commit=False), request.user)
            record.save()
            return redirect(reverse("clinicalrecord_detail", args=[record.pk]))
    else:
        form = ClinicalRecordForm(request=request)
    context = {
        "form": form,
        "specialization": request.user.tenant.get_specialization_display()
        if request.user.tenant
        else "General Practice",
    }
    return render(request, "clinical_records/clinicalrecord_form.html", context)
