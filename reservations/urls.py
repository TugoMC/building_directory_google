# reservation/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("create/<int:professionnel_id>/", views.reservation_create, name="reservation_create"),
    path("success/", views.reservation_success, name="reservation_success"),
]
