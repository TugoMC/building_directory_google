from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm
from .models import Profile
from reservations.models import Reservation  # Ajoutez cette ligne

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # Ajout de request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profiles:profile')
    else:
        form = ProfileForm(instance=profile)
    
    reservations = Reservation.objects.filter(client=request.user).order_by('-created_at')
    
    return render(request, 'profiles/profile.html', {
        'form': form,
        'reservations': reservations
    })