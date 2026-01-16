from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Clinic, Referral, CLINIC_TYPES
from patients.models import Patient
from tenants.models import Tenant
from users.models import CustomUser
from django.contrib import messages
from django.db.models import Q
from common.tenant_scope import scope_queryset, enforce_tenant

@login_required
def referral_list(request):
    referrals = (
        scope_queryset(Referral.objects.select_related("patient", "from_clinic", "to_clinic", "referred_by"), request.user)
        .order_by("-created_at")
        .distinct()
    )
    return render(request, "referrals/list.html", {"referrals": referrals})

@login_required
def create_referral(request):
    clinics = scope_queryset(Clinic.objects.all(), request.user)
    patients = scope_queryset(Patient.objects.all(), request.user)
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        from_clinic_id = request.POST.get("from_clinic")
        to_clinic_id = request.POST.get("to_clinic")
        notes = request.POST.get("notes", "")
        patient = get_object_or_404(Patient, id=patient_id)
        from_clinic = get_object_or_404(Clinic, id=from_clinic_id)
        to_clinic = get_object_or_404(Clinic, id=to_clinic_id)
        Referral.objects.create(
            tenant=from_clinic.tenant,
            patient=patient,
            from_clinic=from_clinic,
            to_clinic=to_clinic,
            referred_by=request.user,
            notes=notes
        )
        messages.success(request, "Referral created successfully.")
        return redirect("referral_list")
    return render(request, "referrals/create.html", {"clinics": clinics, "patients": patients, "clinic_types": CLINIC_TYPES})
