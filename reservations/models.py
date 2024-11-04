from datetime import datetime
import json
from django.db import models
from django.conf import settings
from django.utils import timezone
from professionnels.models import Professionnel
from django.core.exceptions import ValidationError
from reservations.managers import ReservationManager

class ReservationStatus(models.TextChoices):
    PENDING = 'pending', 'En attente de confirmation'
    READY_TO_PAY = 'ready_to_pay', 'Prêt à payer'
    CONFIRMED = 'confirmed', 'Confirmé'
    REFUND_REQUESTED = 'refund_requested', 'Remboursement demandé'
    REFUND_ACCEPTED = 'refund_accepted', 'Remboursement accepté'
    REFUND_REJECTED = 'refund_rejected', 'Remboursement refusé'
    REFUNDED = 'refunded', 'Remboursé'
    COMPLETED = 'completed', 'Terminé'
    CANCELLED = 'cancelled', 'Annulé'
    
    
    
    
class Reservation(models.Model):
    objects = ReservationManager()
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
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        verbose_name="Statut"
    )
    last_status_change = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Dernière modification du statut"
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Prix total",
        help_text="Prix total basé sur le nombre de jours × tarif journalier",
        editable=False
    )

    def cancel(self):
        self.status = ReservationStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Réservation pour {self.professionnel.full_name} par {self.client.username} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=["professionnel", "client", "created_at"], 
                name="unique_reservation"
            )
        ]

    def clean(self):
        super().clean()
        # Vérifier que la transition d'état est valide
        if self.pk:
            old_status = Reservation.objects.get(pk=self.pk).status
            if not self._is_valid_status_transition(old_status, self.status):
                raise ValidationError({
                    'status': f'Transition invalide de {old_status} vers {self.status}'
                })

    def save(self, *args, **kwargs):
        # Si le statut a changé, mettre à jour last_status_change
        if self.pk:
            old_instance = Reservation.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                self.last_status_change = timezone.now()
        super().save(*args, **kwargs)

    def _is_valid_status_transition(self, old_status, new_status):
        """Vérifie si la transition d'état est valide."""
        valid_transitions = {
            ReservationStatus.PENDING: {
                ReservationStatus.READY_TO_PAY,
                ReservationStatus.CANCELLED
            },
            ReservationStatus.READY_TO_PAY: {
                ReservationStatus.CONFIRMED,
                ReservationStatus.CANCELLED
            },
            ReservationStatus.CONFIRMED: {
                ReservationStatus.REFUND_REQUESTED,
                ReservationStatus.COMPLETED,
                ReservationStatus.CANCELLED
            },
            ReservationStatus.REFUND_REQUESTED: {
                ReservationStatus.REFUND_ACCEPTED,
                ReservationStatus.REFUND_REJECTED
            },
            ReservationStatus.REFUND_ACCEPTED: {
                ReservationStatus.REFUNDED
            },
            ReservationStatus.REFUND_REJECTED: {
                ReservationStatus.CONFIRMED  # Retour à l'état confirmé
            },
            ReservationStatus.REFUNDED: set(),  # État final
            ReservationStatus.COMPLETED: set(),  # État final
            ReservationStatus.CANCELLED: set(),  # État final
        }
        return new_status in valid_transitions.get(old_status, set())

    def request_refund(self):
        """Demande un remboursement pour la réservation."""
        if self.status == ReservationStatus.CONFIRMED:
            self.status = ReservationStatus.REFUND_REQUESTED
            self.save()

    def accept_refund(self):
        """Accepte la demande de remboursement."""
        if self.status == ReservationStatus.REFUND_REQUESTED:
            self.status = ReservationStatus.REFUND_ACCEPTED
            self.save()

    def reject_refund(self):
        """Refuse la demande de remboursement."""
        if self.status == ReservationStatus.REFUND_REQUESTED:
            self.status = ReservationStatus.REFUND_REJECTED
            self.save()

    def mark_as_refunded(self):
        """Marque la réservation comme remboursée."""
        if self.status == ReservationStatus.REFUND_ACCEPTED:
            self.status = ReservationStatus.REFUNDED
            self.save()
            
    def mark_as_ready_to_pay(self):
        """Marque la réservation comme prête à payer."""
        if self.status == ReservationStatus.PENDING:
            self.status = ReservationStatus.READY_TO_PAY
            self.save()

    def mark_as_confirmed(self):
        """Marque la réservation comme confirmée après paiement."""
        if self.status == ReservationStatus.READY_TO_PAY:
            self.status = ReservationStatus.CONFIRMED
            self.save()

    def mark_as_completed(self):
        """Marque la réservation comme terminée."""
        if self.status == ReservationStatus.CONFIRMED:
            self.status = ReservationStatus.COMPLETED
            self.save()

    def cancel(self):
        """Annule la réservation."""
        if self.status not in [ReservationStatus.COMPLETED, ReservationStatus.CANCELLED]:
            self.status = ReservationStatus.CANCELLED
            self.save()

    @classmethod
    def update_completed_reservations(cls):
        """
        Met à jour le statut des réservations confirmées dont la date est passée.
        À exécuter via une tâche périodique.
        """
        today = timezone.now().date()
        confirmed_reservations = cls.objects.filter(
            status=ReservationStatus.CONFIRMED
        )
        
        for reservation in confirmed_reservations:
            dates = json.loads(reservation.selected_dates)
            latest_date = max(datetime.strptime(date_str, '%Y-%m-%d').date() 
                            for date_str in dates)
            
            if latest_date < today:
                reservation.mark_as_completed()
                
    
    def calculate_total_price(self):
        if isinstance(self.selected_dates, str):
            dates = json.loads(self.selected_dates)
        else:
            dates = self.selected_dates
        number_of_days = len(dates)
        return self.professionnel.daily_rate * number_of_days

    def save(self, *args, **kwargs):
        # Calculer le prix total
        self.total_price = self.calculate_total_price()
        
        # Code existant pour la mise à jour du statut
        if self.pk:
            old_instance = Reservation.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                self.last_status_change = timezone.now()
        super().save(*args, **kwargs)
        
        
    @classmethod
    def check_date_availability(cls, professionnel, dates_to_check):
        """
        Vérifie si les dates sont disponibles pour un professionnel donné.
        Retourne un tuple (bool, list) : (disponibilité, dates_conflits)
        """
        if isinstance(dates_to_check, str):
            dates_to_check = json.loads(dates_to_check)
            
        dates_to_check = [datetime.strptime(date_str, '%Y-%m-%d').date() 
                         for date_str in dates_to_check]
        
        # Récupérer toutes les réservations confirmées pour ce professionnel
        confirmed_reservations = cls.objects.filter(
            professionnel=professionnel,
            status=ReservationStatus.CONFIRMED
        )
        
        # Vérifier chaque réservation confirmée
        conflicting_dates = []
        for reservation in confirmed_reservations:
            reserved_dates = (json.loads(reservation.selected_dates) 
                            if isinstance(reservation.selected_dates, str) 
                            else reservation.selected_dates)
            
            reserved_dates = [datetime.strptime(date_str, '%Y-%m-%d').date() 
                            for date_str in reserved_dates]
            
            # Trouver les dates qui se chevauchent
            conflicts = set(dates_to_check) & set(reserved_dates)
            conflicting_dates.extend(conflicts)
        
        # Supprimer les doublons et trier les dates
        conflicting_dates = sorted(set(conflicting_dates))
        
        return (len(conflicting_dates) == 0, conflicting_dates)
    
def check_profile_completion(profile):
        """
        Vérifie si les informations essentielles du profil sont complètes.
        """
        return bool(
            profile.first_name and
            profile.last_name and
            profile.city
        )