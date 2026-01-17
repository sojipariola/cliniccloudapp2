from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from referrals.models import Clinic
from clinical_records.models import ClinicalRecord
from appointments.models import Appointment
from patients.models import Patient
from tenants.models import Tenant


@login_required
@permission_required('referrals.view_clinic', raise_exception=True)
def department_overview(request):
    """Admin view: All departments in Central Medical Clinic with their stats."""
    # Get Central Medical Clinic tenant
    central_clinic = get_object_or_404(Tenant, name='Central Medical Clinic')
    
    # Get all clinics (departments) for this tenant
    clinics = Clinic.objects.filter(tenant=central_clinic).annotate(
        patient_count=Count('clinical_records__patient', distinct=True),
        record_count=Count('clinical_records'),
        appointment_count=Count('appointment_clinic', distinct=True)
    ).order_by('name')
    
    context = {
        'central_clinic': central_clinic,
        'clinics': clinics,
        'total_departments': clinics.count(),
        'total_patients': Patient.objects.filter(tenant=central_clinic).count(),
        'total_records': ClinicalRecord.objects.filter(tenant=central_clinic).count(),
        'total_appointments': Appointment.objects.filter(tenant=central_clinic).count(),
    }
    
    return render(request, 'admin/department_overview.html', context)


@login_required
@permission_required('referrals.view_clinic', raise_exception=True)
def department_detail(request, clinic_id):
    """Admin view: Detailed records for a specific department."""
    clinic = get_object_or_404(Clinic, id=clinic_id)
    
    # Get records for this clinic
    clinical_records = ClinicalRecord.objects.filter(
        tenant=clinic.tenant
    ).order_by('-created_at')[:50]  # Last 50 records
    
    # Get appointments for this clinic
    appointments = Appointment.objects.filter(
        tenant=clinic.tenant
    ).order_by('-scheduled_for')[:50]  # Last 50 appointments
    
    # Get unique patients associated with this clinic
    patients = Patient.objects.filter(
        clinical_records__clinic__id=clinic_id
    ).distinct()[:20]
    
    context = {
        'clinic': clinic,
        'clinical_records': clinical_records,
        'appointments': appointments,
        'patients': patients,
        'record_count': ClinicalRecord.objects.filter(tenant=clinic.tenant).count(),
        'patient_count': Patient.objects.filter(tenant=clinic.tenant).distinct().count(),
        'appointment_count': Appointment.objects.filter(tenant=clinic.tenant).count(),
    }
    
    return render(request, 'admin/department_detail.html', context)
