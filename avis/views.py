# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Avis
from .forms import AvisForm
from reservations.models import Reservation, ReservationStatus

@login_required
def avis_create(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, client=request.user)

    # Vérifier si un avis existe déjà
    try:
        existing_avis = Avis.objects.get(reservation=reservation)
        messages.error(request, "Vous avez déjà donné votre avis pour cette réservation.")
        return redirect('avis:avis_list')
    except Avis.DoesNotExist:
        pass

    if request.method == "POST":
        form = AvisForm(request.POST)
        form.instance.reservation = reservation

        if form.is_valid():
            try:
                avis = form.save(commit=False)
                avis.client = request.user
                avis.full_clean()
                avis.save()
                messages.success(request, "Votre avis a été enregistré avec succès.")
                return redirect('avis:avis_list')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            # Handle form errors if necessary
            pass
    else:
        form = AvisForm()

    context = {
        'form': form,
        'reservation': reservation,
        'editing': False
    }
    return render(request, 'avis/avis_form.html', context)

@login_required
def avis_list(request):
    avis_list = Avis.objects.filter(client=request.user)
    return render(request, 'avis/avis_list.html', {
        'avis_list': avis_list
    })

@login_required
def avis_edit(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id, client=request.user)
    
    if request.method == "POST":
        form = AvisForm(request.POST, instance=avis)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre avis a été modifié avec succès.")
            return redirect('avis:avis_list')
    else:
        form = AvisForm(instance=avis)
    
    return render(request, 'avis/avis_form.html', {
        'form': form,
        'avis': avis,
        'editing': True
    })

@login_required
def avis_delete(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id, client=request.user)
    
    if request.method == "POST":
        avis.delete()
        messages.success(request, "Votre avis a été supprimé avec succès.")
        return redirect('avis:avis_list')
        
    return render(request, 'avis/avis_delete.html', {
        'avis': avis
    })

