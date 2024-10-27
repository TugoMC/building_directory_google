from django import forms
from .models import Professionnel

class ProfessionnelForm(forms.ModelForm):
    class Meta:
        model = Professionnel
        fields = [
            'full_name', 'profile_photo', 'email', 'phone', 'city', 
            'commune', 'presentation_video', 'specialization', 
            'skill_level', 'certifications', 'years_of_experience', 
            'daily_rate', 'availability'
        ]
        
        # Ajout de widgets et de labels personnalisés
        widgets = {
            'availability': forms.TextInput(attrs={'placeholder': 'Ex: Lundi, Mardi, Mercredi'}),  # Champ texte pour entrer les jours
            'specialization': forms.Select,
            'skill_level': forms.Select,
        }

        labels = {
            'full_name': 'Nom complet',
            'profile_photo': 'Photo de profil',
            'email': 'Adresse e-mail',
            'phone': 'Numéro de téléphone',
            'city': 'Ville',
            'commune': 'Commune',
            'presentation_video': 'Vidéo de présentation',
            'specialization': 'Spécialisation',
            'skill_level': 'Niveau de compétence',
            'certifications': 'Certifications',
            'years_of_experience': "Années d'expérience",
            'daily_rate': 'Tarif journalier',
            'availability': 'Disponibilité',
            
        }

    def clean_availability(self):
        availability = self.cleaned_data.get('availability')
        if availability:
            # Vérifiez si les jours sont séparés par des virgules
            days = availability.split(',')
            # Validation des jours
            for day in days:
                if day.strip() not in ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']:
                    raise forms.ValidationError("Veuillez entrer des jours valides séparés par des virgules.")
        return availability
