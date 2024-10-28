from django.contrib import admin
from django.utils.html import format_html

from reservations.forms import ReservationAdminForm
from .models import Reservation, ReservationStatus

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    form = ReservationAdminForm
    list_display = ['client', 'professionnel', 'formatted_status', 'created_at', 'last_status_change']
    list_filter = ['status', 'created_at', 'professionnel']
    search_fields = ['client__username', 'professionnel__full_name', 'description']
    readonly_fields = ['created_at', 'last_status_change']
    actions = ['mark_as_ready_to_pay', 'mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']

    def formatted_status(self, obj):
        status_colors = {
            ReservationStatus.PENDING: 'bg-yellow-200',
            ReservationStatus.READY_TO_PAY: 'bg-blue-200',
            ReservationStatus.CONFIRMED: 'bg-green-200',
            ReservationStatus.COMPLETED: 'bg-gray-200',
            ReservationStatus.CANCELLED: 'bg-red-200',
        }
        return format_html(
            '<span class="px-2 py-1 rounded {}">{}</span>',
            status_colors.get(obj.status, ''),
            obj.get_status_display()
        )
    formatted_status.short_description = 'Statut'

    def mark_as_ready_to_pay(self, request, queryset):
        for reservation in queryset:
            if reservation.status == ReservationStatus.PENDING:
                reservation.mark_as_ready_to_pay()
    mark_as_ready_to_pay.short_description = "Marquer comme prêt à payer"

    def mark_as_confirmed(self, request, queryset):
        for reservation in queryset:
            if reservation.status == ReservationStatus.READY_TO_PAY:
                reservation.mark_as_confirmed()
    mark_as_confirmed.short_description = "Marquer comme confirmé"

    def mark_as_completed(self, request, queryset):
        for reservation in queryset:
            if reservation.status == ReservationStatus.CONFIRMED:
                reservation.mark_as_completed()
    mark_as_completed.short_description = "Marquer comme terminé"

    def mark_as_cancelled(self, request, queryset):
        for reservation in queryset:
            reservation.cancel()
    mark_as_cancelled.short_description = "Annuler"