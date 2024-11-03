from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from reservations.models import Reservation
from .models import Notification

@receiver(pre_save, sender=Reservation)
def create_notification_on_status_change(sender, instance, **kwargs):
    if instance.pk:  # Si c'est une mise à jour
        old_instance = Reservation.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # Créer une notification avec les informations du professionnel
            Notification.objects.create(
                user=instance.client,
                title="Mise à jour de votre réservation",
                message=f"Le statut de votre réservation avec {instance.professionnel.full_name} est passé à : {instance.get_status_display()}",
                link=reverse('reservation_list'),
                professional=instance.professionnel.full_name
            )