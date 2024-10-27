# reservation/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from professionnels.models import Professionnel

class Reservation(models.Model):
    professionnel = models.ForeignKey(
        Professionnel, 
        on_delete=models.CASCADE, 
        related_name="reservations"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    description = models.TextField(
        verbose_name="Description de la demande",
        help_text="Décrivez le travail que vous souhaitez faire réaliser"
    )
    phone = models.CharField(
        max_length=20, 
        verbose_name="Numéro de téléphone"
    )
    selected_dates = models.JSONField(
        verbose_name="Dates sélectionnées",
        help_text="Les dates de réservation sélectionnées"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    def __str__(self):
        return f"Réservation pour {self.professionnel.full_name} par {self.client.username}"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=["professionnel", "client", "created_at"], 
                name="unique_reservation"
            )
        ]
