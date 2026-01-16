from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from patients.models import Patient
from .utils import patient_to_fhir

@require_http_methods(["GET"])
def patient_read(request, pk):
    """Return a FHIR Patient resource for the given patient and tenant.

    - For regular users, tenant scoping is enforced via the tenant_id param.
    - Platform admins can omit tenant_id and can fall back to any tenant if the provided tenant_id
      does not match the patient (helps avoid false 404s when ids span tenants).
    """

    tenant_id = request.GET.get("tenant_id")
    is_platform_admin = bool(getattr(request.user, "platform_admin", False))

    if not tenant_id and not is_platform_admin:
        return HttpResponseBadRequest("tenant_id is required")

    base_qs = (
        Patient.objects.select_related("tenant")
        .only(
            "id",
            "tenant_id",
            "first_name",
            "last_name",
            "date_of_birth",
            "email",
            "phone",
        )
    )

    scoped_qs = base_qs
    if tenant_id:
        scoped_qs = scoped_qs.filter(tenant_id=tenant_id)

    try:
        patient = scoped_qs.get(pk=pk)
    except Patient.DoesNotExist:
        if is_platform_admin:
            try:
                patient = base_qs.get(pk=pk)
            except Patient.DoesNotExist as exc:
                raise Http404("Patient not found") from exc
        else:
            raise Http404("Patient not found")

    resource = patient_to_fhir(patient)
    return JsonResponse(
        resource,
        status=200,
        json_dumps_params={"indent": 2},
        content_type="application/fhir+json",
    )
