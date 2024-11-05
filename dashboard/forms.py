# dashboard/forms.py

from django import forms
from professionnels.models import Professionnel
from django.contrib.auth.models import User
from profiles.models import Profile
from reservations.models import Reservation
from portfolios.models import Portfolio, PortfolioImage

class ProfessionnelForm(forms.ModelForm):
    class Meta:
        model = Professionnel
        exclude = []  # Inclure tous les champs
        widgets = {
            'availability': forms.TextInput(attrs={'placeholder': 'Ex: Lundi,Mardi,Mercredi'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'profession', 'city', 'commune', 'profile_image']
        widgets = {
            'profession': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'commune': forms.Select(attrs={'class': 'form-select'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ['created_at', 'last_status_change', 'cancelled_at']
        widgets = {
            'selected_dates': forms.TextInput(attrs={'placeholder': 'Format: ["2024-01-01", "2024-01-02"]'}),
        }

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ['created_at', 'updated_at']

class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['image', 'order']