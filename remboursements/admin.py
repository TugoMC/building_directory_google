from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import RefundRequest

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'reservation_link',
        'requester',
        'wave_number',
        'refund_amount',
        'created_at',
        'processed_at',
        'status',
    ]
    
    list_filter = [
        'processed_at',
        'created_at',
        'processed_by',
    ]
    
    search_fields = [
        'reservation__reference',
        'requester__email',
        'wave_number',
        'reason',
    ]
    
    readonly_fields = [
        'created_at',
        'processed_at',
        'processed_by',
        'refund_amount',
    ]
    
    fieldsets = (
        ('Informations de la demande', {
            'fields': (
                'reservation',
                'requester',
                'reason',
                'wave_number',
                'refund_amount',
            )
        }),
        ('Traitement', {
            'fields': (
                'processed_by',
                'processed_at',
                'rejection_reason',
                'admin_notes',
            )
        }),
    )
    
    def reservation_link(self, obj):
        """Crée un lien vers la page de détail de la réservation"""
        url = reverse(
            'admin:reservations_reservation_change',
            args=[obj.reservation.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.reservation
        )
    reservation_link.short_description = 'Réservation'
    
    def status(self, obj):
        """Affiche le statut de la demande de remboursement"""
        if not obj.processed_at:
            return format_html(
                '<span style="color: orange;">En attente</span>'
            )
        elif obj.rejection_reason:
            return format_html(
                '<span style="color: red;">Refusée</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">Acceptée</span>'
            )
    status.short_description = 'Statut'
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde le modèle en enregistrant l'utilisateur qui traite la demande"""
        if not obj.processed_by and obj.processed_at:
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)
        
    class Media:
        css = {
            'all': ('css/admin/refund_request.css',)
        }