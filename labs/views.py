from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from common.tenant_scope import assign_tenant, enforce_tenant, scope_queryset
from patients.models import Patient

from .forms import LabResultForm
from .models import LabResult


@login_required
@permission_required("labs.change_labresult", raise_exception=True)
def labresult_edit(request, pk):
    result = enforce_tenant(get_object_or_404(LabResult, pk=pk), request.user)
    if request.method == "POST":
        form = LabResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            return redirect(reverse("labresult_detail", args=[result.pk]))
    else:
        form = LabResultForm(instance=result)
    return render(request, "labs/labresult_form.html", {"form": form, "edit": True})


@login_required
@permission_required("labs.delete_labresult", raise_exception=True)
def labresult_delete(request, pk):
    result = enforce_tenant(get_object_or_404(LabResult, pk=pk), request.user)
    if request.method == "POST":
        result.delete()
        return redirect(reverse("labresult_list"))
    return render(request, "labs/labresult_confirm_delete.html", {"result": result})


@login_required
def labresult_list(request):
    results = scope_queryset(
        LabResult.objects.select_related("patient"), request.user
    ).order_by("-created_at")
    
    # Pagination
    paginator = Paginator(results, 10)  # 10 results per page
    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    
    return render(request, "labs/labresult_list.html", {"results": results})


@login_required
def labresult_detail(request, pk):
    result = enforce_tenant(get_object_or_404(LabResult, pk=pk), request.user)
    return render(request, "labs/labresult_detail.html", {"result": result})


@login_required
def labresult_create(request):
    if request.method == "POST":
        form = LabResultForm(request.POST)
        if form.is_valid():
            result = assign_tenant(form.save(commit=False), request.user)
            result.save()
            return redirect(reverse("labresult_detail", args=[result.pk]))
    else:
        form = LabResultForm()
    return render(request, "labs/labresult_form.html", {"form": form})
