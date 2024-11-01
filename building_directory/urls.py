from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('static_pages.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('profiles.urls')),
    path('', include('professionnels.urls')),
    path('reservation/', include('reservations.urls')),
    path('remboursement/', include('remboursements.urls')),
    path('', include('paiements.urls')),
    
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

