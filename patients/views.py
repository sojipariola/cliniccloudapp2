from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import PatientForm
from .models import Patient
from django.contrib.auth.decorators import permission_required, login_required
from common.tenant_scope import scope_queryset, enforce_tenant, assign_tenant

@login_required
@permission_required('patients.change_patient', raise_exception=True)
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
@permission_required('patients.delete_patient', raise_exception=True)
def patient_delete(request, pk):
	patient = enforce_tenant(get_object_or_404(Patient, pk=pk), request.user)
	if request.method == "POST":
		patient.delete()
		return redirect(reverse("patient_list"))
	return render(request, "patients/patient_confirm_delete.html", {"patient": patient})

@login_required
def patient_detail(request, pk):
	patient = enforce_tenant(get_object_or_404(Patient, pk=pk), request.user)
	from clinical_records.models import ClinicalRecord
	clinical_records = scope_queryset(
		ClinicalRecord.objects.filter(patient=patient).order_by('-created_at'),
		request.user
	)
	return render(request, "patients/patient_detail.html", {
		"patient": patient,
		"clinical_records": clinical_records
	})

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
	patients = scope_queryset(Patient.objects.all(), request.user).order_by("last_name", "first_name")
	return render(request, "patients/patient_list.html", {"patients": patients})
