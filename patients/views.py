from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from common.tenant_scope import assign_tenant, enforce_tenant, scope_queryset

from .forms import PatientForm
from .models import Patient


@login_required
@permission_required("patients.change_patient", raise_exception=True)
def patient_edit(request, pk):
    patient = enforce_tenant(get_object_or_404(Patient, pk=pk), request.user)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect(reverse("patient_detail", args=[patient.pk]))
    else:
        form = PatientForm(instance=patient)
    return render(request, "patients/patient_form.html", {"form": form, "edit": True})


@login_required
@permission_required("patients.delete_patient", raise_exception=True)
def patient_delete(request, pk):
    patient = enforce_tenant(get_object_or_404(Patient, pk=pk), request.user)
    if request.method == "POST":
        patient.delete()
        return redirect(reverse("patient_list"))
    return render(request, "patients/patient_confirm_delete.html", {"patient": patient})


@login_required
def patient_detail(request, pk):
    patient = enforce_tenant(get_object_or_404(Patient, pk=pk), request.user)
    # Track recently viewed patients for sidebar quick access
    recent_ids = request.session.get("recent_patients", [])
    if patient.pk in recent_ids:
        recent_ids.remove(patient.pk)
    recent_ids.insert(0, patient.pk)
    request.session["recent_patients"] = recent_ids[:5]
    from clinical_records.models import ClinicalRecord
    from appointments.models import Appointment
    from referrals.models import Referral
    from labs.models import LabResult
    from documents.models import Document

    clinical_records = scope_queryset(
        ClinicalRecord.objects.filter(patient=patient).order_by("-created_at"),
        request.user,
    )
    appointments = scope_queryset(
        Appointment.objects.filter(patient=patient).order_by("-scheduled_for"),
        request.user,
    )
    referrals = scope_queryset(
        Referral.objects.filter(patient=patient).order_by("-id"),
        request.user,
    )
    lab_results = scope_queryset(
        LabResult.objects.filter(patient=patient).order_by("-id"),
        request.user,
    )
    documents = Document.objects.filter(patient=patient).order_by("-uploaded_at")
    return render(
        request,
        "patients/patient_detail.html",
        {
            "patient": patient,
            "clinical_records": clinical_records,
            "appointments": appointments,
            "referrals": referrals,
            "lab_results": lab_results,
            "documents": documents,
        },
    )


@login_required
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = assign_tenant(form.save(commit=False), request.user)
            patient.save()
            return redirect(reverse("patient_detail", args=[patient.pk]))
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form})


@login_required
def patient_list(request):
    patients = scope_queryset(Patient.objects.all(), request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(date_of_birth__icontains=search_query)
        )
    
    patients = patients.order_by("last_name", "first_name")
    
    # Pagination
    paginator = Paginator(patients, 10)  # 10 patients per page
    page = request.GET.get('page')
    try:
        patients = paginator.page(page)
    except PageNotAnInteger:
        patients = paginator.page(1)
    except EmptyPage:
        patients = paginator.page(paginator.num_pages)
    
    return render(request, "patients/patient_list.html", {
        "patients": patients,
        "search_query": search_query
    })
