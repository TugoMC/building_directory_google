# reservation/forms.py
from django import forms
from .models import Reservation
from datetime import date, datetime
import json

class ReservationForm(forms.ModelForm):
    selected_dates = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    class Meta:
        model = Reservation
        fields = ['description', 'phone', 'selected_dates']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none',
                'rows': '4',
                'placeholder': 'Décrivez le travail que vous souhaitez faire réaliser'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none',
                'placeholder': 'XX XX XX XX XX'
            })
        }

    def __init__(self, *args, **kwargs):
        self.professionnel = kwargs.pop('professionnel', None)
        super().__init__(*args, **kwargs)

    def clean_selected_dates(self):
        selected_dates = self.cleaned_data.get('selected_dates')
        if selected_dates:
            try:
                dates = json.loads(selected_dates)
                today = date.today()
                
                # Vérifier chaque date sélectionnée
                for date_str in dates:
                    reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if reservation_date <= today:
                        raise forms.ValidationError(
                            "Vous ne pouvez pas sélectionner la date d'aujourd'hui ou une date passée."
                        )
                
                # Vérifier les conflits de réservation
                is_available, conflicting_dates = Reservation.check_date_availability(
                    self.professionnel, dates
                )
                
                if not is_available:
                    # Formater les dates en conflit pour l'affichage
                    formatted_dates = [d.strftime('%d/%m/%Y') for d in conflicting_dates]
                    dates_str = ", ".join(formatted_dates)
                    raise forms.ValidationError(
                        f"Le professionnel est déjà réservé pour les dates suivantes : {dates_str}"
                    )
                
                return selected_dates
            except json.JSONDecodeError:
                raise forms.ValidationError("Format de dates invalide")
        return selected_dates
    
    
class ReservationAdminForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['professionnel', 'client', 'description', 'phone', 'selected_dates', 'status']

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk:
            old_status = Reservation.objects.get(pk=self.instance.pk).status
            new_status = cleaned_data.get('status')
            if not self.instance._is_valid_status_transition(old_status, new_status):
                self.add_error('status', 
                    f'Transition invalide de {old_status} vers {new_status}'
                )
        return cleaned_data