# reservation/forms.py
from django import forms
from .models import Reservation
from datetime import datetime, timedelta
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
                'placeholder': 'Votre numéro de téléphone'
            })
        }

    def __init__(self, *args, **kwargs):
        self.professionnel = kwargs.pop('professionnel', None)
        super().__init__(*args, **kwargs)

    def clean_selected_dates(self):
        dates = self.cleaned_data.get('selected_dates')
        if not dates:
            raise forms.ValidationError("Veuillez sélectionner au moins une date.")
        
        try:
            dates_list = json.loads(dates)
            if not dates_list:
                raise forms.ValidationError("Veuillez sélectionner au moins une date.")

            # Dictionnaire de conversion français -> anglais pour les jours
            fr_to_en = {
                'Lundi': 'Monday',
                'Mardi': 'Tuesday',
                'Mercredi': 'Wednesday',
                'Jeudi': 'Thursday',
                'Vendredi': 'Friday',
                'Samedi': 'Saturday',
                'Dimanche': 'Sunday'
            }
            
            # Obtenir les jours disponibles en anglais
            available_days = [fr_to_en[day] for day in self.professionnel.get_workdays_list()]
            
            for date_str in dates_list:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    weekday = date_obj.strftime('%A')  # Obtient le jour en anglais
                    
                    if weekday not in available_days:
                        # Conversion inverse pour l'affichage
                        en_to_fr = {v: k for k, v in fr_to_en.items()}
                        jour_fr = en_to_fr[weekday]
                        raise forms.ValidationError(
                            f"Le jour {jour_fr} n'est pas disponible pour ce professionnel."
                        )
                except ValueError:
                    raise forms.ValidationError(f"Le format de la date {date_str} est invalide.")
                    
        except json.JSONDecodeError:
            raise forms.ValidationError("Format de dates invalide.")
            
        return dates
    
    
    


class ReservationAdminForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['professionnel', 'client', 'description', 'phone', 'selected_dates']

    def clean_selected_dates(self):
        dates = self.cleaned_data.get('selected_dates')
        
        # Si les dates sont déjà sous forme de liste, convertissez-les en JSON
        if isinstance(dates, list):
            return json.dumps(dates)

        if not dates:
            raise forms.ValidationError("Veuillez sélectionner au moins une date.")
        
        try:
            dates_list = json.loads(dates)
            if not isinstance(dates_list, list):
                raise forms.ValidationError("Le format des dates sélectionnées doit être une liste.")
        except json.JSONDecodeError:
            raise forms.ValidationError("Format de dates invalide.")
        
        return dates