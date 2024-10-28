# reservation/constants.py
from django.conf import settings

# Configuration de la pagination
RESERVATIONS_PER_PAGE = getattr(settings, 'RESERVATIONS_PER_PAGE', 5)

# Messages
MSG_NO_RESERVATIONS = "Vous n'avez pas encore de réservations."
MSG_FILTER_NO_RESULTS = "Aucune réservation ne correspond à vos critères de recherche."