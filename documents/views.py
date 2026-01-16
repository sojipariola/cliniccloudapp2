from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentUploadForm
from .models import Document
from patients.models import Patient
from referrals.models import Referral
from django.contrib import messages
from common.tenant_scope import scope_queryset, assign_tenant

@login_required
def upload_document(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        # Scope form querysets
        form.fields['patient'].queryset = scope_queryset(Patient.objects.all(), request.user)
        form.fields['referral'].queryset = scope_queryset(Referral.objects.all(), request.user)
        if form.is_valid():
            doc = assign_tenant(form.save(commit=False), request.user)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("upload_document")
    else:
        form = DocumentUploadForm()
        # Scope form querysets for GET request
        form.fields['patient'].queryset = scope_queryset(Patient.objects.all(), request.user)
        form.fields['referral'].queryset = scope_queryset(Referral.objects.all(), request.user)
    return render(request, "documents/upload.html", {"form": form})
