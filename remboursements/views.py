from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.core.exceptions import ValidationError
from .models import RefundRequest
from reservations.models import Reservation
from .forms import RefundRequestForm, RefundProcessForm
from django.db import transaction

class RefundRequestCreateView(LoginRequiredMixin, CreateView):
    model = RefundRequest
    form_class = RefundRequestForm
    template_name = 'remboursements/refund_request_form.html'
    success_url = reverse_lazy('remboursements:refund_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = get_object_or_404(
            Reservation, 
            pk=self.kwargs['reservation_pk']
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        reservation = get_object_or_404(
            Reservation,
            pk=self.kwargs['reservation_pk'],
            client=self.request.user  # Ensure the reservation belongs to the user
        )
        
        try:
            # Create but don't save the form instance
            self.object = form.save(commit=False)
            
            # Set the foreign key fields
            self.object.reservation = reservation
            self.object.requester = self.request.user
            
            # Validate the model
            self.object.full_clean()
            
            # Save the refund request
            self.object.save()
            
            # Update the reservation status
            reservation.request_refund()
            
            messages.success(
                self.request,
                "Votre demande de remboursement a été soumise avec succès."
            )
            
            return super().form_valid(form)
            
        except ValidationError as e:
            form.add_error(None, e)
            messages.error(
                self.request,
                "Erreur lors de la création de la demande de remboursement."
            )
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
        if self.request.user.is_staff and not self.object.processed_at:
            context['process_form'] = RefundProcessForm()
        return context

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