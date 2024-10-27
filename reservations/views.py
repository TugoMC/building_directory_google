from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation, Professionnel
from .forms import ReservationForm
from datetime import datetime, date
import calendar
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def reservation_create(request, professionnel_id):
    professionnel = get_object_or_404(Professionnel, id=professionnel_id)
    
    # Obtenir l'année et le mois depuis l'URL ou utiliser la date actuelle
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    if request.method == "POST":
        logger.info(f"Received POST request for reservation creation. Data: {request.POST}")
        
        # Log the received data
        logger.info(f"Selected dates: {request.POST.get('selected_dates')}")
        logger.info(f"Description: {request.POST.get('description')}")
        logger.info(f"Phone: {request.POST.get('phone')}")
        
        # Pass the professionnel instance to the form
        form = ReservationForm(request.POST, professionnel=professionnel)
        
        if form.is_valid():
            logger.info("Form is valid, proceeding with reservation creation")
            try:
                # Create reservation but don't save yet
                reservation = form.save(commit=False)
                reservation.client = request.user
                reservation.professionnel = professionnel
                
                # Validate selected dates format
                selected_dates = json.loads(form.cleaned_data['selected_dates'])
                logger.info(f"Parsed selected dates: {selected_dates}")
                
                # Save the reservation
                reservation.save()
                logger.info(f"Reservation created successfully with ID: {reservation.id}")
                
                messages.success(request, "Votre réservation a été créée avec succès!")
                return redirect('reservation_success')
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                form.add_error('selected_dates', "Format de dates invalide")
            except Exception as e:
                logger.error(f"Error saving reservation: {e}")
                messages.error(request, "Une erreur est survenue lors de la création de la réservation.")
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ReservationForm(professionnel=professionnel)
    
    # Préparation du calendrier (votre code existant)
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    available_days = set()
    available_weekdays = professionnel.get_workdays_list()
    
    fr_to_en = {
        'Lundi': 'Monday',
        'Mardi': 'Tuesday',
        'Mercredi': 'Wednesday',
        'Jeudi': 'Thursday',
        'Vendredi': 'Friday',
        'Samedi': 'Saturday',
        'Dimanche': 'Sunday'
    }
    
    available_weekdays_en = [fr_to_en[day] for day in available_weekdays]
    
    for week in cal:
        for day in week:
            if day != 0:
                current_date = date(year, month, day)
                if current_date >= date.today() and current_date.strftime('%A') in available_weekdays_en:
                    available_days.add(day)
    
    previous_month_days = []
    if cal[0][0] == 0:
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_month_length = calendar.monthrange(prev_year, prev_month)[1]
        num_days_prev = cal[0].count(0)
        previous_month_days = list(range(prev_month_length - num_days_prev + 1, prev_month_length + 1))
    
    days = [day for week in cal for day in week if day != 0]
    
    context = {
        'form': form,
        'professionnel': professionnel,
        'month_name': month_name,
        'year': year,
        'month': month,
        'days': days,
        'previous_month_days': previous_month_days,
        'current_day': date.today().day if date.today().month == month and date.today().year == year else None,
        'available_days': available_days,
    }
    
    return render(request, 'reservations/reservation_form.html', context)


def reservation_success(request):
    return render(request, "reservations/success.html")