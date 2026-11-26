from django import forms
from django.utils import timezone

from citas.models import Cita

from .models import Consulta, Expediente


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


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['cita', 'diagnostico', 'observaciones']
        labels = {
            'cita': 'Cita (opcional)',
            'diagnostico': 'Diagnóstico',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, medico=None, paciente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cita'].queryset = Cita.objects.filter(
            medico=medico,
            paciente=paciente,
            estado=Cita.Estado.CONFIRMADA,
            consulta__isnull=True,
        )
        self.fields['cita'].required = False
        self.fields['cita'].empty_label = 'Sin cita (consulta no agendada)'
        self.fields['cita'].label_from_instance = lambda c: (
            f'{timezone.localtime(c.inicio):%d/%m/%Y %H:%M} - {c.motivo}'
        )
        for nombre, campo in self.fields.items():
            if nombre == 'cita':
                campo.widget.attrs['class'] = 'form-select'
            else:
                campo.widget.attrs['class'] = 'form-control'

    def clean_diagnostico(self):
        diagnostico = self.cleaned_data['diagnostico'].strip()
        if not diagnostico:
            raise forms.ValidationError('El diagnóstico es obligatorio.')
        return diagnostico