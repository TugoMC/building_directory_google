# views.py
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import ProfileForm
from .models import Profile
from reservations.models import Reservation, ReservationStatus

# views.py
from django.contrib.messages import get_messages
from django.urls import reverse

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!', extra_tags='profile_update')
            return redirect(reverse('profiles:profile'))
    else:
        form = ProfileForm(instance=profile)

    completed_reservations = Reservation.objects.filter(
        client=request.user,
        status=ReservationStatus.COMPLETED
    ).order_by('-last_status_change')

    # Traitement des dates pour chaque réservation
    for reservation in completed_reservations:
        if isinstance(reservation.selected_dates, str):
            try:
                dates_list = json.loads(reservation.selected_dates)
                formatted_dates = []
                for date_str in dates_list:
                    if isinstance(date_str, str) and date_str.strip():
                        try:
                            date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                            formatted_dates.append(date_obj.strftime('%d/%m/%Y'))
                        except ValueError:
                            continue
                reservation.formatted_dates = formatted_dates
            except json.JSONDecodeError:
                reservation.formatted_dates = []
        else:
            reservation.formatted_dates = []

    return render(request, 'profiles/profile.html', {
        'form': form,
        'completed_reservations': completed_reservations
    })