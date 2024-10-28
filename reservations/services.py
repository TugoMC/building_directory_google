from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .constants import RESERVATIONS_PER_PAGE
from .models import Reservation
import logging

logger = logging.getLogger(__name__)

class ReservationService:
    @staticmethod
    def get_filtered_reservations(user, filter_form):
        """
        Récupère les réservations filtrées pour un utilisateur
        """
        reservations = Reservation.objects.filter(client=user)
        
        if filter_form.is_valid():
            cleaned_data = filter_form.cleaned_data
            logger.debug(f"Filter form cleaned data: {cleaned_data}")
            
            # Filtrage par statut
            status = cleaned_data.get('status')
            if status:
                reservations = reservations.filter(status=status)
                logger.debug(f"Filtered by status: {status}")
            
            # Filtrage par date de début
            date_from = cleaned_data.get('date_from')
            if date_from:
                reservations = reservations.filter(created_at__date__gte=date_from)
                logger.debug(f"Filtered by date_from: {date_from}")
            
            # Filtrage par date de fin
            date_to = cleaned_data.get('date_to')
            if date_to:
                reservations = reservations.filter(created_at__date__lte=date_to)
                logger.debug(f"Filtered by date_to: {date_to}")
            
            # Filtrage par recherche
            search = cleaned_data.get('search')
            if search:
                reservations = reservations.filter(
                    Q(professionnel__full_name__icontains=search) |
                    Q(description__icontains=search)
                )
                logger.debug(f"Filtered by search term: {search}")
        else:
            logger.warning(f"Filter form is invalid. Errors: {filter_form.errors}")
        
        logger.debug(f"Final query: {reservations.query}")
        return reservations.order_by('-created_at')

    @staticmethod
    def paginate_reservations(reservations, page_number):
        """
        Pagine les réservations
        """
        paginator = Paginator(reservations, RESERVATIONS_PER_PAGE)
        logger.debug(f"Total items: {paginator.count}, Total pages: {paginator.num_pages}")

        try:
            page_obj = paginator.page(page_number)
            logger.debug(f"Current page: {page_obj.number}")
        except PageNotAnInteger:
            page_obj = paginator.page(1)
            logger.debug("Invalid page number, defaulting to page 1")
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            logger.debug(f"Empty page, showing last page: {paginator.num_pages}")

        return page_obj