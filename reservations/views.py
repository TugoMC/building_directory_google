from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation, Professionnel, ReservationStatus, check_profile_completion
from .forms import ReservationForm
from datetime import datetime, date, timedelta
import calendar
import json
import logging
from .filters import ReservationFilterForm
from .services import ReservationService
from .constants import MSG_NO_RESERVATIONS, MSG_FILTER_NO_RESULTS

logger = logging.getLogger(__name__)

@login_required
def reservation_create(request, professionnel_id):
    
    profile = request.user.profile
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not check_profile_completion(profile):
            missing_info = []
            if not profile.first_name:
                missing_info.append("Prénom")
            if not profile.last_name:
                missing_info.append("Nom")
            if not profile.city:
                missing_info.append("Ville")
                
            return JsonResponse({
                'error': 'Profile incomplete',
                'missing_info': missing_info
            }, status=400)
        return JsonResponse({'success': True})



   
    professionnel = get_object_or_404(Professionnel, id=professionnel_id)
    
    # Obtenir l'année et le mois depuis l'URL ou utiliser la date actuelle
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    reserved_dates = set()
    confirmed_reservations = Reservation.objects.filter(
        professionnel=professionnel,
        status=ReservationStatus.CONFIRMED
    )
    
    for reservation in confirmed_reservations:
        dates = (json.loads(reservation.selected_dates) 
                if isinstance(reservation.selected_dates, str) 
                else reservation.selected_dates)
        for date_str in dates:
            reserved_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if reserved_date.year == year and reserved_date.month == month:
                reserved_dates.add(reserved_date.day)
    
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
                reservation.status = ReservationStatus.PENDING
                
                # Validate selected dates format
                selected_dates = json.loads(form.cleaned_data['selected_dates'])
                logger.info(f"Parsed selected dates: {selected_dates}")
                
                # Save the reservation
                reservation.save()
                logger.info(f"Reservation created successfully with ID: {reservation.id}")
                
                messages.success(request, "Votre réservation a été créée avec succès ! Elle est en attente de confirmation.")
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
    
    # Préparation du calendrier
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
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    for week in cal:
        for day in week:
            if day != 0:
                current_date = date(year, month, day)
                # Vérifier que la date est à partir de demain et est un jour ouvrable
                if current_date >= tomorrow and current_date.strftime('%A') in available_weekdays_en:
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
        'reserved_dates': reserved_dates,
    }
    
    return render(request, 'reservations/reservation_form.html', context)

@login_required
def reservation_success(request):
    return render(request, "reservations/success.html")



@login_required
def reservation_list(request):
    logger.debug("Starting reservation_list view")
    logger.debug(f"GET parameters: {request.GET}")
    
    # Initialiser le formulaire de filtrage avec les données de la requête
    filter_form = ReservationFilterForm(request.GET or None)
    logger.debug(f"Filter form is bound: {filter_form.is_bound}")
    
    
    # Récupérer les réservations filtrées
    reservations = ReservationService.get_filtered_reservations(
        user=request.user,
        filter_form=filter_form
    )
    logger.debug(f"Number of reservations before pagination: {reservations.count()}")
    
    # Paginer les résultats
    page_obj = ReservationService.paginate_reservations(
        reservations=reservations,
        page_number=request.GET.get('page')
    )
    
    # Préparer le message si aucun résultat
    if not reservations.exists():
        if filter_form.is_bound and any(filter_form.cleaned_data.values() if filter_form.is_valid() else []):
            messages.info(request, MSG_FILTER_NO_RESULTS)
            logger.debug("No results found with active filters")
        else:
            messages.info(request, MSG_NO_RESERVATIONS)
            logger.debug("No reservations found")
    
    context = {
        'filter_form': filter_form,
        'page_obj': page_obj,
        'has_filters': filter_form.is_bound and any(filter_form.cleaned_data.values() if filter_form.is_valid() else [])
    }
    
    logger.debug("Rendering reservation list template")
    return render(request, 'reservations/reservation_list.html', context)



@login_required
def reservation_delete(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, client=request.user)
    
    if request.method == "POST":
        reservation.cancel()  # Utilisation de la méthode cancel() existante
        messages.success(request, "Votre réservation a été annulée avec succès.")
        return redirect('reservation_list')
        
    return render(request, 'reservations/reservation_delete.html', {
        'reservation': reservation
    })
    