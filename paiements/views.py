from django.shortcuts import render, get_object_or_404
from reservations.models import Reservation
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

def payment_details(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    selected_dates = json.dumps(json.loads(reservation.selected_dates))
    return render(request, 'paiements/payment_details.html', {
        'reservation': reservation,
        'selected_dates': selected_dates
    })
    



def payment_process(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        # Logique de traitement du paiement ici
        # Par exemple, avec une passerelle de paiement comme Stripe ou Paypal
        
        # Si le paiement est réussi :
        reservation.mark_as_confirmed()
        messages.success(request, "Votre réservation a bien été confirmée.")
        return redirect(reverse('reservation_list'))
        
        # Sinon, afficher un message d'erreur :
        # messages.error(request, "Une erreur est survenue lors du paiement.")
    
    return render(request, 'paiements/payment_process.html', {
        'reservation': reservation
    })