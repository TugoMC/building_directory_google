# urls.py
from django.urls import path
from .views import ProfessionnelListView, ProfessionnelDetailView

urlpatterns = [
    path('professionnels/', ProfessionnelListView.as_view(), name='professionnels_list'),
    path('professionnel/<int:pk>/', ProfessionnelDetailView.as_view(), name='professionnel_detail'),
]