from django.urls import path
from . import views

app_name = 'paiements'
urlpatterns = [
    path('reservation/<int:reservation_id>/', views.payment_details, name='payment_details'),
    path('reservation/<int:reservation_id>/process/', views.payment_process, name='payment_process'),
]