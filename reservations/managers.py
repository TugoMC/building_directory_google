# reservation/managers.py
from django.db import models
from django.db.models import Q

class ReservationQuerySet(models.QuerySet):
    def filter_by_params(self, params):
        """
        Filtre les réservations selon les paramètres fournis
        """
        queryset = self

        if params.get('status'):
            queryset = queryset.filter(status=params['status'])

        if params.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=params['date_from'])

        if params.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=params['date_to'])

        if params.get('search'):
            search_query = params['search']
            queryset = queryset.filter(
                Q(professionnel__full_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset

class ReservationManager(models.Manager):
    def get_queryset(self):
        return ReservationQuerySet(self.model, using=self._db)

    def filter_by_params(self, params):
        return self.get_queryset().filter_by_params(params)