# views.py
from django.views.generic import ListView, DetailView
from .models import Professionnel
from django.db.models import Q
from calendar import monthrange
from datetime import datetime
from .models import Professionnel
from django.db.models import Q
from calendar import monthrange
from datetime import datetime, date
import calendar
from django.http import JsonResponse

class ProfessionnelListView(ListView):
    model = Professionnel
    template_name = 'professionnels/professionnels_list.html'
    context_object_name = 'professionnels'
    paginate_by = 6

    def get_queryset(self):
        queryset = Professionnel.objects.all()
        
        # Filtrage par ville
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city=city)
            
        # Filtrage par spécialisation
        specialization = self.request.GET.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization=specialization)
            
        # Filtrage par niveau de compétence
        skill_level = self.request.GET.get('skill_level')
        if skill_level:
            queryset = queryset.filter(skill_level=skill_level)
            
        # Filtrage par disponibilité
        availability = self.request.GET.get('availability')
        if availability:
            queryset = queryset.filter(availability__contains=[availability])
            
        # Recherche par nom
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(specialization__icontains=search_query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = Professionnel.CITY_CHOICES
        context['specializations'] = Professionnel.SPECIALIZATIONS
        context['skill_levels'] = Professionnel.SkillLevel.choices
        context['availability_choices'] = [
            ("Lundi", "Lundi"),
            ("Mardi", "Mardi"),
            ("Mercredi", "Mercredi"),
            ("Jeudi", "Jeudi"),
            ("Vendredi", "Vendredi"),
            ("Samedi", "Samedi"),
            ("Dimanche", "Dimanche")
        ]
        return context


    


class ProfessionnelDetailView(DetailView):
    model = Professionnel
    template_name = 'professionnels/professionnels_detail.html'
    context_object_name = 'professionnel'

    def get_calendar_data(self, year, month):
        # Obtenir le nombre de jours dans le mois
        _, num_days = monthrange(year, month)
        
        # Obtenir les jours de disponibilité du professionnel
        workdays = self.object.get_workdays_list()
        available_days = []
        
        # Convertir les noms de jours en français vers l'anglais pour la comparaison
        fr_to_en = {
            'Lundi': 'Monday',
            'Mardi': 'Tuesday',
            'Mercredi': 'Wednesday',
            'Jeudi': 'Thursday',
            'Vendredi': 'Friday',
            'Samedi': 'Saturday',
            'Dimanche': 'Sunday'
        }
        
        en_workdays = [fr_to_en[day.strip()] for day in workdays]
        
        # Pour chaque jour du mois
        for day in range(1, num_days + 1):
            current_date = date(year, month, day)
            if current_date.strftime('%A') in en_workdays:
                available_days.append(day)
        
        # Calculer les jours du mois précédent
        first_day_weekday = date(year, month, 1).weekday()
        
        if first_day_weekday > 0:
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            _, prev_num_days = monthrange(prev_year, prev_month)
            previous_month_days = list(range(prev_num_days - first_day_weekday + 1, prev_num_days + 1))
        else:
            previous_month_days = []
            
        return {
            'days': list(range(1, num_days + 1)),
            'current_day': date.today().day if date.today().year == year and date.today().month == month else None,
            'month_name': calendar.month_name[month] + f" {year}",
            'available_days': available_days,
            'previous_month_days': previous_month_days
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenir le mois et l'année actuels par défaut
        current_date = datetime.now()
        context.update(self.get_calendar_data(current_date.year, current_date.month))
        
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Si c'est une requête AJAX pour mettre à jour le calendrier
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            year = int(request.GET.get('year'))
            month = int(request.GET.get('month'))
            calendar_data = self.get_calendar_data(year, month)
            return JsonResponse(calendar_data)
            
        return super().get(request, *args, **kwargs)