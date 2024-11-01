from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import RefundRequest
from reservations.models import Reservation
from .forms import RefundRequestForm, RefundProcessForm
from django.db import transaction
import logging
import traceback
from functools import wraps


# Configuration du logger
logger = logging.getLogger('refund_system')
logger.setLevel(logging.DEBUG)

# Handler pour écrire dans un fichier
file_handler = logging.FileHandler('refund_requests.log')
file_handler.setLevel(logging.DEBUG)

# Handler pour la console avec un format plus concis
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Format détaillé pour les logs
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s\n'
    'Request ID: %(request_id)s\n'
    'User: %(user)s\n'
    'Reservation: %(reservation_id)s\n'
    'Data: %(data)s\n'
    '%(details)s\n'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_request_id():
    """Génère un ID unique pour chaque requête"""
    import uuid
    return str(uuid.uuid4())[:8]

class RefundLogger:
    def __init__(self, view_instance):
        self.view = view_instance
        self.request_id = get_request_id()
        self.base_extra = {
            'request_id': self.request_id,
            'user': 'Anonymous',
            'reservation_id': 'N/A',
            'data': {},
            'details': ''
        }

    def update_base_extra(self):
        if hasattr(self.view, 'request'):
            self.base_extra.update({
                'user': str(getattr(self.view.request, 'user', 'Anonymous')),
                'data': {
                    'method': self.view.request.method,
                    'path': self.view.request.path,
                }
            })
        if hasattr(self.view, 'kwargs'):
            self.base_extra['reservation_id'] = self.view.kwargs.get('reservation_pk', 'N/A')

    def get_form_details(self, form):
        """Extrait les détails pertinents du formulaire"""
        return {
            'is_bound': form.is_bound,
            'is_valid': form.is_valid() if form.is_bound else 'Not bound',
            'errors': dict(form.errors) if form.is_bound else {},
            'cleaned_data': form.cleaned_data if form.is_bound and form.is_valid() else {},
            'fields': list(form.fields.keys())
        }

    def log(self, level, message, extra=None, exc_info=None):
        """Méthode centralisée pour le logging"""
        self.update_base_extra()
        log_extra = self.base_extra.copy()
        if extra:
            log_extra.update(extra)
        logger.log(level, message, extra=log_extra, exc_info=exc_info)

def with_refund_logging(func):
    """Décorateur amélioré pour le logging des opérations de remboursement"""
    @wraps(func)
    def wrapper(view_instance, *args, **kwargs):
        refund_logger = RefundLogger(view_instance)
        
        try:
            # Log de début
            refund_logger.log(
                logging.INFO,
                f"Début de {func.__name__}"
            )
            
            # Si c'est une méthode de formulaire
            if 'form' in kwargs:
                form = kwargs['form']
                refund_logger.log(
                    logging.DEBUG,
                    "Détails du formulaire",
                    {'details': refund_logger.get_form_details(form)}
                )
            
            result = func(view_instance, *args, **kwargs)
            
            # Log de succès
            refund_logger.log(
                logging.INFO,
                f"Succès de {func.__name__}",
                {'details': 'Opération terminée avec succès'}
            )
            
            return result
            
        except ValidationError as e:
            refund_logger.log(
                logging.ERROR,
                "Erreur de validation",
                {
                    'details': {
                        'error_type': 'ValidationError',
                        'error_message': str(e),
                        'validation_errors': e.message_dict if hasattr(e, 'message_dict') else {'__all__': [str(e)]}
                    }
                },
                exc_info=True
            )
            raise
            
        except Exception as e:
            refund_logger.log(
                logging.ERROR,
                "Erreur inattendue",
                {
                    'details': {
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'traceback': traceback.format_exc()
                    }
                },
                exc_info=True
            )
            raise
    
    return wrapper

class RefundRequestCreateView(LoginRequiredMixin, CreateView):
    model = RefundRequest
    form_class = RefundRequestForm
    template_name = 'remboursements/refund_request_form.html'
    success_url = reverse_lazy('remboursements:refund_request_list')

    def get_form_kwargs(self):
        """Ajoute la réservation aux kwargs du formulaire"""
        kwargs = super().get_form_kwargs()
        reservation = get_object_or_404(
            Reservation,
            pk=self.kwargs['reservation_pk'],
            client=self.request.user
        )
        kwargs['reservation'] = reservation
        return kwargs

    @with_refund_logging
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = get_object_or_404(
            Reservation, 
            pk=self.kwargs['reservation_pk']
        )
        
        RefundLogger(self).log(
            logging.DEBUG,
            "Réservation récupérée",
            {
                'details': {
                    'reservation_status': reservation.status,
                    'total_price': str(reservation.total_price),
                    'client': str(reservation.client)
                }
            }
        )
        
        context['reservation'] = reservation
        return context

    @with_refund_logging
    @transaction.atomic
    def form_valid(self, form):
        refund_logger = RefundLogger(self)
        
        try:
            # La réservation est déjà associée au formulaire via get_form_kwargs
            self.object = form.save(commit=False)
            self.object.requester = self.request.user
            self.object.save()
            
            # Mise à jour du statut de la réservation
            self.object.reservation.request_refund()
            
            refund_logger.log(
                logging.INFO,
                "Demande de remboursement créée avec succès",
                {
                    'details': {
                        'refund_request_id': self.object.id,
                        'amount': str(self.object.refund_amount),
                        'created_at': str(self.object.created_at)
                    }
                }
            )
            
            return redirect(self.get_success_url())

        except ValidationError as e:
            refund_logger.log(
                logging.ERROR,
                "Échec de la création de la demande",
                {'details': {'validation_errors': str(e)}}
            )
            form.add_error(None, str(e))
            return self.form_invalid(form)

    
        
class RefundRequestListView(LoginRequiredMixin, ListView):
    model = RefundRequest
    template_name = 'remboursements/refund_request_list.html'
    context_object_name = 'refund_requests'

    def get_queryset(self):
        if self.request.user.is_staff:
            return RefundRequest.objects.all()
        return RefundRequest.objects.filter(requester=self.request.user)

class RefundRequestDetailView(LoginRequiredMixin, DetailView):
    model = RefundRequest
    template_name = 'remboursements/refund_request_detail.html'
    context_object_name = 'refund_request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenir la réservation directement depuis l'objet RefundRequest
        context['reservation'] = self.object.reservation
        return context

    def get_queryset(self):
        # Filtrer les demandes de remboursement pour n'afficher que celles
        # de l'utilisateur connecté, sauf pour le staff qui peut tout voir
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(requester=self.request.user)
        return qs
      
class ProcessRefundView(UserPassesTestMixin, UpdateView):
    model = RefundRequest
    form_class = RefundProcessForm
    template_name = 'remboursements/process_refund.html'
    success_url = reverse_lazy('remboursements:refund_request_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.processed_at:
            raise ValidationError("Cette demande a déjà été traitée.")
        return obj

    def form_valid(self, form):
        refund_request = self.get_object()
        action = form.cleaned_data['action']
        
        try:
            if action == 'accept':
                refund_request.accept(
                    self.request.user,
                    form.cleaned_data['admin_notes']
                )
                messages.success(
                    self.request,
                    "La demande de remboursement a été acceptée."
                )
            else:
                refund_request.reject(
                    self.request.user,
                    form.cleaned_data['rejection_reason'],
                    form.cleaned_data['admin_notes']
                )
                messages.warning(
                    self.request,
                    "La demande de remboursement a été refusée."
                )
            
            return redirect(self.success_url)
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)