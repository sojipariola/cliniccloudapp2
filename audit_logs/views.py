from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from audit_logs.models import AuditLog
from common.tenant_scope import scope_queryset

@login_required
def audit_log_list(request):
    logs = scope_queryset(AuditLog.objects.all(), request.user).order_by('-timestamp')[:100]
    return render(request, "audit_logs/list.html", {"logs": logs})
