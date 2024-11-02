# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from reservations.models import Reservation, ReservationStatus

class Avis(models.Model):
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='avis'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avis'
    )
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note sur 5"
    )
    commentaire = models.TextField(
        verbose_name="Commentaire"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.client.username} - {self.note}/5"

    def clean(self):
        if not self.reservation_id:
            raise ValidationError("La réservation est requise.")
            
        if self.reservation.status != ReservationStatus.COMPLETED:
            raise ValidationError("Vous ne pouvez donner un avis que sur une réservation terminée.")
            
        if self.client_id and self.reservation.client_id != self.client_id:
            raise ValidationError("Vous ne pouvez donner un avis que sur vos propres réservations.")