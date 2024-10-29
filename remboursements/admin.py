from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import RefundRequest

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_client',
        'get_professionnel',
        'refund_amount',
        'created_at',
        'get_status',
        'get_reservation_link',
        'processed_at',
        'processed_by'
    ]
    
    list_filter = [
        'created_at',
        'processed_at',
        ('processed_by', admin.RelatedOnlyFieldListFilter),
        'reservation__status'
    ]
    
    search_fields = [
        'reservation__client__email',
        'reservation__client__username',
        'reservation__professionnel__user__email',
        'wave_number',
        'reason'
    ]
    
    readonly_fields = [
        'created_at',
        'processed_at',
        'processed_by',
        'get_reservation_details',
        'refund_amount'
    ]
    
    fieldsets = [
        ('Informations de la demande', {
            'fields': (
                'reservation',
                'get_reservation_details',
                'requester',
                'reason',
                'wave_number',
                'refund_amount',
                'created_at'
            )
        }),
        ('Traitement de la demande', {
            'fields': (
                'processed_by',
                'processed_at',
                'admin_notes',
                'rejection_reason'
            )
        })
    ]
    
    def get_client(self, obj):
        return obj.reservation.client.email
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'reservation__client__email'
    
    def get_professionnel(self, obj):
        return obj.reservation.professionnel.user.email
    get_professionnel.short_description = 'Professionnel'
    get_professionnel.admin_order_field = 'reservation__professionnel__user__email'
    
    def get_status(self, obj):
        status = obj.reservation.status
        status_colors = {
            'refund_requested': 'orange',
            'refund_accepted': 'green',
            'refund_rejected': 'red',
            'refunded': 'blue'
        }
        color = status_colors.get(status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.reservation.get_status_display()
        )
    get_status.short_description = 'Statut'
    get_status.admin_order_field = 'reservation__status'
    
    def get_reservation_link(self, obj):
        url = reverse(
            'admin:reservations_reservation_change',
            args=[obj.reservation.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"Réservation #{obj.reservation.id}"
        )
    get_reservation_link.short_description = 'Lien réservation'
    
    def get_reservation_details(self, obj):
        if obj.reservation:
            return format_html(
                """
                <div style="margin: 10px 0;">
                    <strong>Client:</strong> {}<br>
                    <strong>Professionnel:</strong> {}<br>
                    <strong>Prix total:</strong> {} FCFA<br>
                    <strong>Dates:</strong> {}<br>
                    <strong>Statut:</strong> {}<br>
                </div>
                """,
                obj.reservation.client.email,
                obj.reservation.professionnel.user.email,
                obj.reservation.total_price,
                obj.reservation.selected_dates,
                obj.reservation.get_status_display()
            )
        return "-"
    get_reservation_details.short_description = 'Détails de la réservation'
    
    def save_model(self, request, obj, form, change):
        if not obj.processed_by and 'rejection_reason' in form.changed_data:
            obj.processed_by = request.user
            obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Les demandes de remboursement ne peuvent être créées que par les utilisateurs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression des demandes de remboursement
        return False
    
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }