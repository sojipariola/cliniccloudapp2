from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from common.audit import log_audit
from users.models import CustomUser


@staff_member_required
def pending_users(request):
    users = CustomUser.objects.filter(is_active=False)
    return render(request, "admin/pending_users.html", {"users": users})


@staff_member_required
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id, is_active=False)
    user.is_active = True
    user.save()
    log_audit(
        "user_approved",
        user=user,
        tenant=user.tenant,
        details=f"User {user.username} approved by {request.user.username}.",
    )
    messages.success(request, f"User {user.username} has been approved and activated.")
    return redirect("pending_users")
