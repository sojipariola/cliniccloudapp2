from django.urls import path

from . import views

urlpatterns = [
    path('departments/', views.department_overview, name='department_overview'),
    path('departments/<int:clinic_id>/', views.department_detail, name='department_detail'),
]
