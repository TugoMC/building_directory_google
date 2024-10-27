from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('static_pages.urls')),
    path('accounts/', include('allauth.urls')),
]
