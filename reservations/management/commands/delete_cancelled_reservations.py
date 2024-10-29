from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservations.models import Reservation, ReservationStatus

class Command(BaseCommand):
    help = 'Supprime les réservations annulées de plus de 14 jours'

    def handle(self, *args, **options):
        deleted_count = Reservation.objects.filter(
            status=ReservationStatus.CANCELLED,
            cancelled_at__lte=timezone.now() - timedelta(days=14)
        ).delete()[0]
        self.stdout.write(f"{deleted_count} réservations annulées ont été supprimées")