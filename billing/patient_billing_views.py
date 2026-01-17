"""Views for patient billing (invoices for services/procedures)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from common.tenant_scope import enforce_tenant, scope_queryset
from patients.models import Patient
from .models import PatientInvoice, InvoiceLineItem


@login_required
@require_http_methods(["GET"])
def patient_billing(request, patient_pk):
    """View invoices for a specific patient."""
    patient = enforce_tenant(get_object_or_404(Patient, pk=patient_pk), request.user)
    
    invoices = scope_queryset(
        PatientInvoice.objects.filter(patient=patient).order_by("-issued_date"),
        request.user,
    )
    
    total_owed = sum(
        inv.total for inv in invoices if inv.status in ["sent", "overdue"]
    )
    
    context = {
        "patient": patient,
        "invoices": invoices,
        "total_owed": total_owed,
    }
    return render(request, "billing/patient_invoices.html", context)


@login_required
@require_http_methods(["GET"])
def patient_invoice_detail(request, invoice_pk):
    """View invoice details."""
    invoice = get_object_or_404(PatientInvoice, pk=invoice_pk)
    enforce_tenant(invoice.patient, request.user)
    enforce_tenant(invoice, request.user)
    
    context = {
        "invoice": invoice,
        "items": invoice.items.all(),
    }
    return render(request, "billing/patient_invoice_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def patient_invoice_create(request, patient_pk):
    """Create a new invoice for a patient."""
    patient = enforce_tenant(get_object_or_404(Patient, pk=patient_pk), request.user)
    
    if not request.user.has_perm("billing.add_patientinvoice"):
        messages.error(request, "You don't have permission to create invoices.")
        return redirect("patient_detail", pk=patient_pk)
    
    if request.method == "GET":
        context = {"patient": patient}
        return render(request, "billing/patient_invoice_form.html", context)
    
    # POST: Create invoice
    try:
        invoice_number = request.POST.get("invoice_number")
        due_date = request.POST.get("due_date")
        tax = request.POST.get("tax", 0)
        notes = request.POST.get("notes", "")
        
        invoice = PatientInvoice.objects.create(
            tenant=request.user.tenant,
            patient=patient,
            invoice_number=invoice_number,
            due_date=due_date,
            tax=float(tax),
            notes=notes,
        )
        
        # Add line items
        item_count = int(request.POST.get("item_count", 0))
        for i in range(item_count):
            description = request.POST.get(f"item_{i}_description")
            service_type = request.POST.get(f"item_{i}_service_type", "other")
            quantity = request.POST.get(f"item_{i}_quantity", 1)
            unit_price = request.POST.get(f"item_{i}_unit_price", 0)
            
            if description and unit_price:
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=description,
                    service_type=service_type,
                    quantity=float(quantity),
                    unit_price=float(unit_price),
                )
        
        messages.success(request, f"Invoice {invoice_number} created successfully.")
        return redirect("patient_invoice_detail", invoice_pk=invoice.pk)
    
    except Exception as e:
        messages.error(request, f"Error creating invoice: {str(e)}")
        return redirect("patient_billing", patient_pk=patient_pk)


@login_required
@require_http_methods(["POST"])
def patient_invoice_mark_paid(request, invoice_pk):
    """Mark an invoice as paid."""
    invoice = get_object_or_404(PatientInvoice, pk=invoice_pk)
    enforce_tenant(invoice, request.user)
    
    if not request.user.has_perm("billing.change_patientinvoice"):
        messages.error(request, "You don't have permission to update invoices.")
        return redirect("patient_invoice_detail", invoice_pk=invoice_pk)
    
    from datetime import date
    invoice.status = "paid"
    invoice.paid_date = date.today()
    invoice.save()
    
    messages.success(request, f"Invoice {invoice.invoice_number} marked as paid.")
    return redirect("patient_invoice_detail", invoice_pk=invoice_pk)
