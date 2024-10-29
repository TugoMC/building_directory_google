from django.db import models
from django.conf import settings
from reservations.models import Reservation, ReservationStatus
from django.core.exceptions import ValidationError
import re

def validate_wave_number(value):
    pass

class RefundRequest(models.Model):
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='refund_request'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refund_requests'
    )
    reason = models.TextField(
        verbose_name="Motif du remboursement",
        help_text="Veuillez expliquer la raison de votre demande de remboursement"
    )
    wave_number = models.CharField(
        max_length=20,
        verbose_name="Numéro Wave",
        help_text="Votre numéro Wave Mobile",
        validators=[validate_wave_number]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_refunds'
    )
    admin_notes = models.TextField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,  # Make this field nullable
        blank=True  # Allow blank
    )

    def clean(self):
        if not self.reservation_id:
            raise ValidationError("Une réservation doit être spécifiée")
            
        if self.reservation.status != ReservationStatus.CONFIRMED:
            raise ValidationError(
                "Seules les réservations confirmées peuvent faire l'objet d'une demande de remboursement"
            )

    def save(self, *args, **kwargs):
        if not self.pk and self.reservation:  # Only on creation
            self.refund_amount = self.reservation.total_price
            # Don't call request_refund here, we'll do it in the view
        super().save(*args, **kwargs)
               
        

    def accept(self, admin_user, notes=None):
        """Accepte la demande de remboursement"""
        from django.utils import timezone
        
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.admin_notes = notes
        self.save()
        self.reservation.accept_refund()

    def reject(self, admin_user, rejection_reason, notes=None):
        """Refuse la demande de remboursement"""
        from django.utils import timezone
        
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.rejection_reason = rejection_reason
        self.admin_notes = notes
        self.save()
        self.reservation.reject_refund()

    def __str__(self):
        return f"Demande de remboursement pour {self.reservation}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de remboursement"
        verbose_name_plural = "Demandes de remboursement"
        
        