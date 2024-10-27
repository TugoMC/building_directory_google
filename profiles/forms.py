from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['last_name', 'first_name', 'profession', 'city', 'commune']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre tous les champs optionnels
        for field in self.fields.values():
            field.required = False
        
        # Initialiser les choix depuis les constantes du modèle
        self.fields['profession'].choices = Profile.PROFESSION_CHOICES
        self.fields['city'].choices = [('', '---------')] + list(Profile.CITY_CHOICES)
        self.fields['commune'].choices = [('', '---------')] + list(Profile.COMMUNE_CHOICES)