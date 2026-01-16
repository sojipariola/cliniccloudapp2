from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tenants.models import Tenant
from ai.note_taking import generate_clinical_note

@login_required
def ai_note(request):
    ai_note = None
    transcript = ''
    specialization = request.user.tenant.specialization if request.user.tenant else 'general_practice'
    
    # Get all specialization choices for display
    specialization_choices = Tenant.SPECIALIZATION_CHOICES
    
    if request.method == "POST":
        transcript = request.POST.get("transcript", "")
        # Use posted specialization or default to tenant's specialization
        specialization = request.POST.get("specialization", specialization)
        
        if transcript and specialization:
            ai_note = generate_clinical_note(transcript, specialization)
    
    return render(request, "clinical_records/ai_note.html", {
        "ai_note": ai_note,
        "transcript": transcript,
        "specialization": specialization,
        "specialization_choices": specialization_choices,
        "tenant_specialization": request.user.tenant.specialization if request.user.tenant else 'general_practice',
    })
