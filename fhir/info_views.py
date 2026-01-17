from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def fhir_info(request):
    """Display FHIR API information and documentation."""
    return render(request, "fhir/fhir_info.html")
