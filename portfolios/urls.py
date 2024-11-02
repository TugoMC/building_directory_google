# portfolios/urls.py
from django.urls import path
from .views import PortfolioDetailView

app_name = 'portfolios'

urlpatterns = [
    path('<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),
]
