from django.db import models

from patients.models import Patient
from tenants.models import Tenant


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    interval = models.CharField(
        max_length=20, choices=[("monthly", "Monthly"), ("yearly", "Yearly")]
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TenantSubscription(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    last_payment = models.DateTimeField(null=True, blank=True)
    next_payment_due = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tenant} - {self.plan}"


class Payment(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="payments"
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    is_subscription = models.BooleanField(default=False)
    external_id = models.CharField(max_length=100, blank=True)  # For gateway reference

    def __str__(self):
        return f"{self.tenant} - {self.amount} {self.currency} ({'Subscription' if self.is_subscription else 'One-time'})"


class PatientInvoice(models.Model):
    """Invoice for services/procedures provided to a patient."""
    
    INVOICE_STATUS = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="patient_invoices")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default="draft")
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="GBP")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-issued_date"]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient} - £{self.total}"
    
    def calculate_total(self):
        """Calculate total from line items."""
        self.subtotal = sum(item.total for item in self.items.all())
        self.total = self.subtotal + self.tax
        return self.total


class InvoiceLineItem(models.Model):
    """Line item for a patient invoice."""
    
    invoice = models.ForeignKey(PatientInvoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    service_type = models.CharField(
        max_length=50,
        choices=[
            ("consultation", "Consultation"),
            ("procedure", "Procedure"),
            ("test", "Lab Test"),
            ("medication", "Medication"),
            ("imaging", "Imaging"),
            ("other", "Other"),
        ],
        default="other"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update invoice total
        self.invoice.calculate_total()
        self.invoice.save()
    
    def __str__(self):
        return f"{self.description} - £{self.total}"
