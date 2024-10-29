# remboursements/urls.py
from django.urls import path
from . import views

app_name = 'remboursements'

urlpatterns = [
    path('demande/<int:reservation_pk>/', 
         views.RefundRequestCreateView.as_view(), 
         name='refund_request_create'),
    path('liste/', 
         views.RefundRequestListView.as_view(), 
         name='refund_request_list'),
    path('detail/<int:pk>/', 
         views.RefundRequestDetailView.as_view(), 
         name='refund_request_detail'),
    path('traiter/<int:pk>/', 
         views.ProcessRefundView.as_view(), 
         name='process_refund'),
]