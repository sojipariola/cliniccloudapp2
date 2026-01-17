from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from audit_logs.models import AuditLog
from common.tenant_scope import scope_queryset


@login_required
def audit_log_list(request):
    logs = scope_queryset(AuditLog.objects.all(), request.user).order_by("-timestamp")
    
    # Pagination
    paginator = Paginator(logs, 10)  # 10 logs per page
    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)
    
    return render(request, "audit_logs/list.html", {"logs": logs})
