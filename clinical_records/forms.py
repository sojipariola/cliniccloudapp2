from django import forms
from .models import ClinicalRecord
from .clinic_note_types import CLINIC_NOTE_TEMPLATES

class ClinicalRecordForm(forms.ModelForm):
    class Meta:
        model = ClinicalRecord
        fields = ["patient", "note_type", "note"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "note_type": forms.Select(attrs={"class": "form-control", "id": "id_note_type"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 10, "id": "id_note"})
        }
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Get specialization from tenant
        if request and hasattr(request, 'user') and request.user.tenant:
            specialization = request.user.tenant.specialization
            # Get available note types for this specialization
            available_notes = CLINIC_NOTE_TEMPLATES.get(specialization, CLINIC_NOTE_TEMPLATES.get('general_practice', []))
            self.fields['note_type'].choices = [(note, note) for note in available_notes]
            self.specialization = specialization
        else:
            # Fallback to general practice
            default_notes = CLINIC_NOTE_TEMPLATES.get('general_practice', [])
            self.fields['note_type'].choices = [(note, note) for note in default_notes]
    
    def clean_note_type(self):
        """Validate note_type is in available templates"""
        note_type = self.cleaned_data.get('note_type')
        if hasattr(self, 'specialization'):
            available_types = CLINIC_NOTE_TEMPLATES.get(self.specialization, [])
            if note_type not in available_types:
                raise forms.ValidationError("Invalid note type for this clinic specialization.")
        return note_type
