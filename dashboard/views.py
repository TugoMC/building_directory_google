
from datetime import datetime
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from portfolios.models import Portfolio, PortfolioImage
from professionnels.models import Professionnel
from reservations.forms import StatusUpdateForm
from reservations.models import Reservation, ReservationStatus
from .forms import (
    ProfessionnelForm,
    ProfileForm,
    ReservationForm,
    PortfolioForm,
    PortfolioImageForm
)


@staff_member_required  # Sécurité : Accessible uniquement aux membres du staff
def dashboard_home(request):
    context = {
        'professionals_count': Professionnel.objects.count(),
        'users_count': User.objects.count(),
        'reservations_count': Reservation.objects.count(),
        'portfolios_count': Portfolio.objects.count(),
        'recent_reservations': Reservation.objects.order_by('-created_at')[:5],
        'last_update': timezone.now(),
    }
    return render(request, 'dashboard/home.html', context)

# Vues pour les Professionnels
@staff_member_required
def professional_list(request):
    search_query = request.GET.get('search', '')
    professionals = Professionnel.objects.all()
    
    if search_query:
        professionals = professionals.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )
    
    professionals = professionals.order_by('-id')
    paginator = Paginator(professionals, 10)
    page = request.GET.get('page')
    professionals = paginator.get_page(page)
    
    return render(request, 'dashboard/professional_list.html', {
        'professionals': professionals,
        'search_query': search_query
    })

@staff_member_required
def professional_create(request):
    if request.method == 'POST':
        form = ProfessionnelForm(request.POST, request.FILES)
        if form.is_valid():
            professional = form.save()
            messages.success(request, 'Professionnel créé avec succès.')
            return redirect('dashboard:professional_list')
    else:
        form = ProfessionnelForm()
    
    return render(request, 'dashboard/professional_form.html', {'form': form})

@staff_member_required
def professional_edit(request, pk):
    professional = get_object_or_404(Professionnel, pk=pk)
    if request.method == 'POST':
        form = ProfessionnelForm(request.POST, request.FILES, instance=professional)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professionnel mis à jour avec succès.')
            return redirect('dashboard:professional_list')
    else:
        form = ProfessionnelForm(instance=professional)
    
    return render(request, 'dashboard/professional_form.html', {
        'form': form,
        'professional': professional
    })
    
@staff_member_required
def professional_delete(request, pk):
    professional = get_object_or_404(Professionnel, pk=pk)
    if request.method == 'POST':
        professional.delete()
        messages.success(request, 'Professionnel supprimé avec succès.')
        return redirect('dashboard:professional_list')
    
    return render(request, 'dashboard/professional_confirm_delete.html', {
        'professional': professional
    })
    
@staff_member_required
def professional_detail(request, pk):
    professional = get_object_or_404(Professionnel, pk=pk)
    return render(request, 'dashboard/professional_detail.html', {
        'professional': professional
    })

# Vues pour les Profils
@staff_member_required
def profile_list(request):
    search_query = request.GET.get('search', '')
    profiles = User.objects.all()
    
    if search_query:
        profiles = profiles.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(profiles, 10)
    page = request.GET.get('page')
    profiles = paginator.get_page(page)
    
    return render(request, 'dashboard/profile_list.html', {
        'profiles': profiles,
        'search_query': search_query
    })

@staff_member_required
def profile_edit(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('dashboard:profile_list')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'dashboard/profile_form.html', {
        'form': form,
        'profile': profile
    })

@staff_member_required
def profile_delete(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Profil supprimé avec succès.')
        return redirect('dashboard:profile_list')
    return render(request, 'dashboard/profile_confirm_delete.html', {'profile': profile})

@staff_member_required
def profile_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile
    return render(request, 'dashboard/profile_detail.html', {
        'user': user,
        'profile': profile
    })

# Vues pour les Réservations
@staff_member_required
def reservation_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    reservations = Reservation.objects.all()
    
    if search_query:
        reservations = reservations.filter(
            Q(client__username__icontains=search_query) |
            Q(professionnel__full_name__icontains=search_query)
        )
    
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    reservations = reservations.order_by('-created_at')
    paginator = Paginator(reservations, 10)
    page = request.GET.get('page')
    reservations = paginator.get_page(page)
    
    return render(request, 'dashboard/reservation_list.html', {
        'reservations': reservations,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': ReservationStatus.choices  # Utilisez directement ReservationStatus
    })

@staff_member_required
def reservation_create(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()
            messages.success(request, 'Réservation créée avec succès.')
            return redirect('dashboard:reservation_list')
    else:
        form = ReservationForm()
    
    return render(request, 'dashboard/reservation_form.html', {
        'form': form,
        'is_creation': True
    })
    
@staff_member_required
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Réservation mise à jour avec succès.')
            return redirect('dashboard:reservation_list')
    else:
        form = ReservationForm(instance=reservation)
    
    return render(request, 'dashboard/reservation_form.html', {
        'form': form,
        'reservation': reservation
    })

@staff_member_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Réservation supprimée avec succès.')
        return redirect('dashboard:reservation_list')
    return render(request, 'dashboard/reservation_confirm_delete.html', {
        'reservation': reservation
    })
    
@staff_member_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Préparer les dates
    selected_dates = []
    if reservation.selected_dates:
        try:
            if isinstance(reservation.selected_dates, str):
                dates = json.loads(reservation.selected_dates)
            else:
                dates = reservation.selected_dates
            selected_dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
        except (json.JSONDecodeError, ValueError):
            messages.error(request, "Erreur lors du chargement des dates")
    
    # Créer le formulaire de statut
    status_form = StatusUpdateForm(
        initial={'status': reservation.status},
        reservation=reservation
    )
    
    # Récupérer l'historique complet des changements de statut
    status_history = reservation.status_history.all()
    
        
    context = {
        'reservation': reservation,
        'status_history': status_history,
        'selected_dates': selected_dates,
        'can_edit': reservation.status not in [
            ReservationStatus.COMPLETED,
            ReservationStatus.CANCELLED,
            ReservationStatus.REFUNDED
        ],
        'status_form': status_form
    }
    
    return render(request, 'dashboard/reservation_detail.html', context)

@staff_member_required
def reservation_status_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, reservation=reservation)
        if form.is_valid():
            try:
                new_status = form.cleaned_data['status']
                reservation.status = new_status
                reservation.save()
                messages.success(request, 'Statut de la réservation mis à jour avec succès.')
            except Exception as e:
                messages.error(request, f'Erreur lors de la mise à jour du statut: {str(e)}')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            
    return redirect('dashboard:reservation_detail', pk=pk)



# Vues pour les Portfolios
@staff_member_required
def portfolio_list(request):
    search_query = request.GET.get('search', '')
    professionnel_id = request.GET.get('professionnel_id', None)

    # Filtre de base
    portfolios = Portfolio.objects.select_related('professionnel').all()

    # Filtrer par mot-clé
    if search_query:
        portfolios = portfolios.filter(
            Q(title__icontains=search_query) |
            Q(professionnel__full_name__icontains=search_query)
        )

    # Filtrer par professionnel si sélectionné
    if professionnel_id:
        portfolios = portfolios.filter(professionnel_id=professionnel_id)

    portfolios = portfolios.order_by('-created_at')
    paginator = Paginator(portfolios, 9)
    page = request.GET.get('page')
    portfolios = paginator.get_page(page)
    
    # Récupération de tous les professionnels pour le filtre
    professionnels = Professionnel.objects.all()
    
    return render(request, 'dashboard/portfolio_list.html', {
        'portfolios': portfolios,
        'search_query': search_query,
        'professionnels': professionnels,  # Liste des professionnels
        'selected_professionnel_id': professionnel_id,  # ID du professionnel sélectionné
    })


@staff_member_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save()
            # Gestion des images
            for img in request.FILES.getlist('images'):
                PortfolioImage.objects.create(
                    portfolio=portfolio,
                    image=img,
                    order=PortfolioImage.objects.filter(portfolio=portfolio).count()
                )
            messages.success(request, 'Portfolio créé avec succès.')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = PortfolioForm()
    
    return render(request, 'dashboard/portfolio_form.html', {
        'form': form,
        'is_creation': True
    })

@staff_member_required
def portfolio_edit(request, pk):
    portfolio = get_object_or_404(Portfolio.objects.select_related('professionnel'), pk=pk)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            portfolio = form.save()
            # Gestion des nouvelles images
            for img in request.FILES.getlist('images'):
                PortfolioImage.objects.create(
                    portfolio=portfolio,
                    image=img,
                    order=portfolio.images.count()
                )
            messages.success(request, 'Portfolio mis à jour avec succès.')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = PortfolioForm(instance=portfolio)
    
    return render(request, 'dashboard/portfolio_form.html', {
        'form': form,
        'portfolio': portfolio,
        'images': portfolio.images.all().order_by('order'),
        'is_creation': False
    })
    
@staff_member_required
def portfolio_delete(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, 'Portfolio supprimé avec succès.')
        return redirect('dashboard:portfolio_list')
    return render(request, 'dashboard/portfolio_confirm_delete.html', {
        'portfolio': portfolio
    })

# Amélioration des vues de gestion des images
@staff_member_required
@require_POST
def portfolio_image_add(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
    form = PortfolioImageForm(request.POST, request.FILES)
    
    if form.is_valid():
        image = form.save(commit=False)
        image.portfolio = portfolio
        image.order = portfolio.images.count()  # Place la nouvelle image à la fin
        image.save()
        return JsonResponse({
            'success': True, 
            'message': 'Image ajoutée avec succès'
        })
    
    return JsonResponse({
        'success': False, 
        'errors': form.errors
    }, status=400)

@staff_member_required
@require_POST
def portfolio_image_reorder(request, portfolio_id):
    try:
        portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
        order_data = json.loads(request.body)
        
        with transaction.atomic():
            for index, image_id in enumerate(order_data['image_order']):
                PortfolioImage.objects.filter(
                    portfolio=portfolio,
                    id=image_id
                ).update(order=index)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
      
@staff_member_required
@require_POST
def portfolio_image_delete(request, image_id):
    image = get_object_or_404(PortfolioImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})  # Toujours renvoyer un JSON pour que le front puisse traiter la réponse
  
