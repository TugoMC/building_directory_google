# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Vue principale du dashboard
    path('', views.dashboard_home, name='home'),
    
    # URLs pour Professionnels
    path('professionals/', views.professional_list, name='professional_list'),
    path('professionals/create/', views.professional_create, name='professional_create'),
    path('professional/<int:pk>/', views.professional_detail, name='professional_detail'),
    path('professionals/<int:pk>/edit/', views.professional_edit, name='professional_edit'),
    path('professionals/<int:pk>/delete/', views.professional_delete, name='professional_delete'),
    
    # URLs pour Profils
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<int:pk>/edit/', views.profile_edit, name='profile_edit'),
    path('profiles/<int:pk>/delete/', views.profile_delete, name='profile_delete'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    
    # URLs pour Réservations
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/edit/', views.reservation_edit, name='reservation_edit'),
    path('reservations/<int:pk>/delete/', views.reservation_delete, name='reservation_delete'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/status/', views.reservation_status_update, name='reservation_status_update'),
    
    # URLs pour Portfolios
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolios/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolios/<int:pk>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('portfolios/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
    path('portfolio/image/<int:image_id>/delete/', views.portfolio_image_delete, name='portfolio_image_delete'),
]