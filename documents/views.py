from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from common.tenant_scope import assign_tenant, enforce_tenant, scope_queryset
from patients.models import Patient
from referrals.models import Referral

from .forms import DocumentUploadForm
from .models import Document


@login_required
def document_detail(request, pk):
    """View a single document with PDF viewer and navigation."""
    document = enforce_tenant(get_object_or_404(Document, pk=pk), request.user)
    return render(request, "documents/document_detail.html", {"document": document})


@login_required
def upload_document(request):
    patient = None
    patient_id = request.GET.get('patient')
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
    
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        # Scope form querysets
        form.fields["patient"].queryset = scope_queryset(
            Patient.objects.all(), request.user
        )
        form.fields["referral"].queryset = scope_queryset(
            Referral.objects.all(), request.user
        )
        if form.is_valid():
            doc = assign_tenant(form.save(commit=False), request.user)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, "Document uploaded successfully.")
            if patient:
                return redirect("patient_detail", pk=patient.pk)
            return redirect("upload_document")
    else:
        form = DocumentUploadForm()
        # Scope form querysets for GET request
        form.fields["patient"].queryset = scope_queryset(
            Patient.objects.all(), request.user
        )
        form.fields["referral"].queryset = scope_queryset(
            Referral.objects.all(), request.user
        )
        # Pre-select patient if provided
        if patient:
            form.fields["patient"].initial = patient
    return render(request, "documents/upload.html", {"form": form, "patient": patient})
