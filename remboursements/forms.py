from django import forms
from .models import RefundRequest

from django import forms
from .models import RefundRequest

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['reason', 'wave_number']
        widgets = {
            'reason': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control'
                }
            ),
            'wave_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+225 XX XX XX XX XX'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and not self.instance.pk and self.reservation:
            self.instance.reservation = self.reservation
        
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.reservation:
            raise forms.ValidationError("Une réservation doit être spécifiée")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class RefundProcessForm(forms.Form):
    ACTIONS = [
        ('accept', 'Accepter'),
        ('reject', 'Refuser'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTIONS,
        widget=forms.RadioSelect,
        label="Action"
    )
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Motif du refus"
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Notes administratives"
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')

        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError(
                "Le motif du refus est obligatoire en cas de rejet"
            )
        return cleaned_data