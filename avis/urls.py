# avis/urls.py
from django.urls import path
from . import views

app_name = 'avis'  # Namespace pour les URLs

urlpatterns = [
    path('create/<int:reservation_id>/', views.avis_create, name='avis_create'),
    path('edit/<int:avis_id>/', views.avis_edit, name='avis_edit'),
    path('delete/<int:avis_id>/', views.avis_delete, name='avis_delete'),
    path('list/', views.avis_list, name='avis_list'),
]