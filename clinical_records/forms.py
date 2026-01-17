from django import forms

from .clinic_note_types import CLINIC_NOTE_TEMPLATES
from .models import ClinicalRecord


class ClinicalRecordForm(forms.ModelForm):
    class Meta:
        model = ClinicalRecord
        fields = [
            "patient",
            "note_type",
            "chief_complaint",
            "history_of_present_illness",
            "past_medical_history",
            "medications_history",
            "allergy_history",
            "physical_exam_inspection",
            "physical_exam_palpation",
            "physical_exam_percussion",
            "physical_exam_auscultation",
            "provisional_diagnosis",
            "investigations_ordered",
            "investigation_results",
            "assessment_diagnosis",
            "plan",
            "note",
        ]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "note_type": forms.Select(
                attrs={"class": "form-control", "id": "id_note_type"}
            ),
            "chief_complaint": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Brief description of patient's main complaint"}
            ),
            "history_of_present_illness": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Detailed timeline and characteristics of illness"}
            ),
            "past_medical_history": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Significant past medical conditions and treatments"}
            ),
            "medications_history": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Current and recent medications"}
            ),
            "allergy_history": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Known allergies (medications, food, environmental)"}
            ),
            "physical_exam_inspection": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Observation findings (appearance, color, scars, etc.)"}
            ),
            "physical_exam_palpation": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Findings from touch and pressure examination"}
            ),
            "physical_exam_percussion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Findings from tapping examination"}
            ),
            "physical_exam_auscultation": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Findings from listening with stethoscope"}
            ),
            "provisional_diagnosis": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Working diagnosis based on initial findings"}
            ),
            "investigations_ordered": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Tests and investigations to be performed"}
            ),
            "investigation_results": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Results of investigations and tests"}
            ),
            "assessment_diagnosis": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Final assessment and confirmed diagnosis"}
            ),
            "plan": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Treatment plan, medications, referrals, follow-up"}
            ),
            "note": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "id": "id_note", "placeholder": "General notes"}
            ),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Get specialization from tenant
        if request and hasattr(request, "user") and request.user.tenant:
            specialization = request.user.tenant.specialization
            # Get available note types for this specialization
            available_notes = CLINIC_NOTE_TEMPLATES.get(
                specialization, CLINIC_NOTE_TEMPLATES.get("general_practice", [])
            )
            self.fields["note_type"].choices = [
                (note, note) for note in available_notes
            ]
            self.specialization = specialization
        else:
            # Fallback to general practice
            default_notes = CLINIC_NOTE_TEMPLATES.get("general_practice", [])
            self.fields["note_type"].choices = [(note, note) for note in default_notes]

    def clean_note_type(self):
        """Validate note_type is in available templates"""
        note_type = self.cleaned_data.get("note_type")
        if hasattr(self, "specialization"):
            available_types = CLINIC_NOTE_TEMPLATES.get(self.specialization, [])
            if note_type not in available_types:
                raise forms.ValidationError(
                    "Invalid note type for this clinic specialization."
                )
        return note_type
