from django import forms

from .models import Expediente


class ExpedienteForm(forms.ModelForm):
    version_esperada = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Expediente
        fields = ['grupo_sanguineo', 'alergias', 'antecedentes']
        labels = {
            'grupo_sanguineo': 'Grupo sanguíneo',
            'alergias': 'Alergias',
            'antecedentes': 'Antecedentes médicos',
        }
        widgets = {
            'alergias': forms.Textarea(attrs={'rows': 3}),
            'antecedentes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre, campo in self.fields.items():
            if nombre == 'grupo_sanguineo':
                campo.widget.attrs['class'] = 'form-select'
            elif nombre != 'version_esperada':
                campo.widget.attrs['class'] = 'form-control'