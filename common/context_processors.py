from patients.models import Patient


def recent_patients(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"recent_patients_sidebar": []}

    recent_ids = request.session.get("recent_patients", [])
    if not recent_ids:
        return {"recent_patients_sidebar": []}

    qs = Patient.objects.filter(id__in=recent_ids)
    if not getattr(user, "platform_admin", False):
        qs = qs.filter(tenant=getattr(user, "tenant", None))

    patients = list(qs)
    patients.sort(key=lambda p: recent_ids.index(p.id))
    return {"recent_patients_sidebar": patients[:5]}
