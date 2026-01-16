

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Appointment
from patients.models import Patient
from .forms import AppointmentForm
from django.contrib.auth.decorators import login_required, permission_required
from common.tenant_scope import scope_queryset, enforce_tenant, assign_tenant

@login_required
def appointment_list(request):
	appointments = (
		scope_queryset(Appointment.objects.select_related("patient"), request.user)
		.order_by("scheduled_for")
	)
	return render(request, "appointments/appointment_list.html", {"appointments": appointments})

@login_required
def appointment_detail(request, pk):
	appointment = enforce_tenant(get_object_or_404(Appointment, pk=pk), request.user)
	return render(request, "appointments/appointment_detail.html", {"appointment": appointment})

@login_required
def appointment_create(request):
	if request.method == "POST":
		form = AppointmentForm(request.POST)
		if form.is_valid():
			appointment = assign_tenant(form.save(commit=False), request.user)
			appointment.save()
			return redirect(reverse("appointment_detail", args=[appointment.pk]))
	else:
		form = AppointmentForm()
	return render(request, "appointments/appointment_form.html", {"form": form})

@login_required
@permission_required('appointments.change_appointment', raise_exception=True)
def appointment_edit(request, pk):
	appointment = enforce_tenant(get_object_or_404(Appointment, pk=pk), request.user)
	if request.method == "POST":
		form = AppointmentForm(request.POST, instance=appointment)
		if form.is_valid():
			form.save()
			return redirect(reverse("appointment_detail", args=[appointment.pk]))
	else:
		form = AppointmentForm(instance=appointment)
	return render(request, "appointments/appointment_form.html", {"form": form, "edit": True})

@login_required
@permission_required('appointments.delete_appointment', raise_exception=True)
def appointment_delete(request, pk):
	appointment = get_object_or_404(Appointment, pk=pk)
	if request.method == "POST":
		appointment.delete()
		return redirect(reverse("appointment_list"))
	return render(request, "appointments/appointment_confirm_delete.html", {"appointment": appointment})