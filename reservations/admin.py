# reservation/admin.py
from django.contrib import admin
from .models import Reservation
from .forms import ReservationAdminForm
import json

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    form = ReservationAdminForm
    list_display = ('professionnel', 'client', 'created_at', 'phone', 'display_selected_dates')
    list_filter = ('created_at', 'professionnel')
    search_fields = ('client__username', 'professionnel__full_name', 'description')
    ordering = ['-created_at']
    
    def display_selected_dates(self, obj):
        # Vérifiez si les dates sont stockées sous forme de chaîne JSON
        if isinstance(obj.selected_dates, str):
            return ", ".join(json.loads(obj.selected_dates))
        elif isinstance(obj.selected_dates, list):
            return ", ".join(obj.selected_dates)
        return "Aucune date"
    display_selected_dates.short_description = "Dates sélectionnées"
