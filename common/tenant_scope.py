from django.core.exceptions import PermissionDenied


def scope_queryset(queryset, user):
	"""Return queryset scoped to user's tenant unless platform admin."""
	if getattr(user, "platform_admin", False):
		return queryset
	return queryset.filter(tenant=user.tenant)


def enforce_tenant(obj, user):
	"""Ensure object belongs to user's tenant unless platform admin."""
	if getattr(user, "platform_admin", False):
		return obj
	if getattr(obj, "tenant_id", None) and obj.tenant_id != getattr(user.tenant, "id", None):
		raise PermissionDenied("You do not have access to this tenant's data.")
	return obj


def assign_tenant(obj, user):
	"""Set tenant on new objects for non-platform admins."""
	if getattr(obj, "tenant_id", None) is None and hasattr(user, "tenant"):
		obj.tenant = user.tenant
	return obj