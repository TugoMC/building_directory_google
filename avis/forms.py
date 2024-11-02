# forms.py
from django import forms
from .models import Avis

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            'commentaire': forms.Textarea(attrs={'rows': 4}),
        }

