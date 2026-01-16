
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import ClinicalRecord
from patients.models import Patient
from .forms import ClinicalRecordForm
from django.contrib.auth.decorators import login_required, permission_required
from common.tenant_scope import scope_queryset, enforce_tenant, assign_tenant

@login_required
@permission_required('clinical_records.change_clinicalrecord', raise_exception=True)
def clinicalrecord_edit(request, pk):
	record = enforce_tenant(get_object_or_404(ClinicalRecord, pk=pk), request.user)
	if request.method == "POST":
		form = ClinicalRecordForm(request.POST, instance=record, request=request)
		if form.is_valid():
			form.save()
			return redirect(reverse("clinicalrecord_detail", args=[record.pk]))
	else:
		form = ClinicalRecordForm(instance=record, request=request)
	context = {
		"form": form, 
		"edit": True,
		"specialization": request.user.tenant.get_specialization_display() if request.user.tenant else "General Practice"
	}
	return render(request, "clinical_records/clinicalrecord_form.html", context)

@login_required
@permission_required('clinical_records.delete_clinicalrecord', raise_exception=True)
def clinicalrecord_archive(request, pk):
	record = enforce_tenant(get_object_or_404(ClinicalRecord, pk=pk), request.user)
	if request.method == "POST":
		record.note = "[ARCHIVED] " + record.note
		record.save()
		return redirect(reverse("clinicalrecord_list"))
	return render(request, "clinical_records/clinicalrecord_confirm_archive.html", {"record": record})

@login_required
def clinicalrecord_list(request):
	records = (
		scope_queryset(ClinicalRecord.objects.select_related("patient"), request.user)
		.order_by("-created_at")
	)
	return render(request, "clinical_records/clinicalrecord_list.html", {"records": records})

@login_required
def clinicalrecord_detail(request, pk):
	record = enforce_tenant(get_object_or_404(ClinicalRecord, pk=pk), request.user)
	return render(request, "clinical_records/clinicalrecord_detail.html", {"record": record})

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
		"specialization": request.user.tenant.get_specialization_display() if request.user.tenant else "General Practice"
	}
	return render(request, "clinical_records/clinicalrecord_form.html", context)
