# Placeholder for AI note-taking integration
# In production, connect to an LLM or medical AI API

from clinical_records.clinic_note_types import CLINIC_NOTE_TEMPLATES


def get_specialization_context(specialization):
    """
    Return specialization-specific context for AI note generation.
    This helps guide the AI to generate appropriate content.
    """
    contexts = {
        "general_practice": "General practice visit with primary care focus",
        "pediatrics": "Pediatric patient care with growth and development tracking",
        "dental": "Dental procedure and oral health assessment",
        "eye": "Ophthalmologic examination and vision assessment",
        "womens_health": "Women's health and gynecologic care",
        "dermatology": "Dermatologic condition assessment and treatment",
        "mental_health": "Mental health and psychiatric evaluation",
        "physiotherapy": "Physical therapy and rehabilitation assessment",
        "orthopedic": "Orthopedic surgical consultation and joint assessment",
        "cardiology": "Cardiac examination and cardiovascular assessment",
        "ent": "Ear, nose, and throat examination",
        "urology": "Urologic condition assessment",
        "oncology": "Oncology patient care and cancer treatment",
        "allergy": "Allergy testing and immunology assessment",
        "pain": "Pain management and chronic pain assessment",
        "gastroenterology": "Gastrointestinal examination and assessment",
        "endocrinology": "Endocrine and metabolic disorder assessment",
        "neurology": "Neurological examination and assessment",
        "surgical": "General surgery consultation and surgical planning",
        "urgent_care": "Urgent care evaluation",
        "multi_specialty": "Multi-specialty consultation",
        "telemedicine": "Remote telemedicine consultation",
        "community_health": "Community health outreach and assessment",
        "fertility": "Fertility and reproductive health assessment",
        "geriatric": "Geriatric care for elderly patients",
    }
    return contexts.get(specialization, "General clinical assessment")


def generate_clinical_note(transcript, specialization):
    """
    Given a transcript (from telemedicine or dictation) and specialization,
    return a structured clinical note using the template for that specialization.
    """
    template = CLINIC_NOTE_TEMPLATES.get(
        specialization, CLINIC_NOTE_TEMPLATES.get("general_practice", [])
    )
    context = get_specialization_context(specialization)

    # In production, call an LLM or medical AI API here with specialization context
    # For now, return a dict with template sections and placeholder content
    note_sections = {}
    for section in template:
        note_sections[
            section
        ] = f"[AI-generated {section} - specialization: {specialization}]\n{section} details would be populated here based on transcript analysis."

    return {
        "sections": note_sections,
        "specialization": specialization,
        "context": context,
        "transcript": transcript,
    }
