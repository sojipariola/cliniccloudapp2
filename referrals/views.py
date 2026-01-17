from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from common.tenant_scope import enforce_tenant, scope_queryset
from patients.models import Patient
from tenants.models import Tenant
from users.models import CustomUser

from .models import CLINIC_TYPES, Clinic, Referral


@login_required
def referral_list(request):
    referrals = (
        scope_queryset(
            Referral.objects.select_related(
                "patient", "from_clinic", "to_clinic", "referred_by"
            ),
            request.user,
        )
        .order_by("-created_at")
        .distinct()
    )
    
    # Pagination
    paginator = Paginator(referrals, 10)  # 10 referrals per page
    page = request.GET.get('page')
    try:
        referrals = paginator.page(page)
    except PageNotAnInteger:
        referrals = paginator.page(1)
    except EmptyPage:
        referrals = paginator.page(paginator.num_pages)
    
    return render(request, "referrals/list.html", {"referrals": referrals})


@login_required
def create_referral(request):
    patient_id = request.GET.get('patient')
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
        # Use patient's tenant to get clinics when patient is pre-selected
        clinics = Clinic.objects.filter(tenant=patient.tenant)
    else:
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
            notes=notes,
        )
        messages.success(request, "Referral created successfully.")
        if patient_id:
            return redirect("patient_detail", pk=patient_id)
        return redirect("referral_list")
    
    return render(
        request,
        "referrals/create.html",
        {
            "clinics": clinics,
            "patients": patients,
            "patient": patient,
            "clinic_types": CLINIC_TYPES
        },
    )
