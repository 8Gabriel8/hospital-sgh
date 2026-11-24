from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from pacientes.models import Paciente

from .models import Cita

User = get_user_model()


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = [
            'paciente', 'medico', 'inicio', 'duracion_min',
            'motivo', 'urgencia_menor',
        ]
        labels = {
            'paciente': 'Paciente',
            'medico': 'Médico',
            'inicio': 'Fecha y hora',
            'duracion_min': 'Duración (minutos)',
            'motivo': 'Motivo de la consulta',
            'urgencia_menor': 'Urgencia menor',
        }
        widgets = {
            'inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(
            activo=True
        ).order_by('apellido_paterno', 'nombre')
        self.fields['medico'].queryset = User.objects.filter(
            groups__name='Médico', is_active=True
        ).order_by('first_name', 'username')
        self.fields['medico'].label_from_instance = (
            lambda u: f'Dr(a). {u.get_full_name() or u.username}'
        )
        self.fields['inicio'].input_formats = ['%Y-%m-%dT%H:%M']
        for nombre, campo in self.fields.items():
            if nombre == 'urgencia_menor':
                campo.widget.attrs['class'] = 'form-check-input'
            elif nombre in ('paciente', 'medico'):
                campo.widget.attrs['class'] = 'form-select'
            else:
                campo.widget.attrs['class'] = 'form-control'

    def clean_inicio(self):
        inicio = self.cleaned_data['inicio']
        if inicio <= timezone.now():
            raise forms.ValidationError('La cita debe ser en una fecha y hora futuras.')
        return inicio

    def clean_duracion_min(self):
        duracion = self.cleaned_data['duracion_min']
        if duracion < 5 or duracion > 240:
            raise forms.ValidationError('La duración debe estar entre 5 y 240 minutos.')
        return duracion

    def clean(self):
        datos = super().clean()
        medico = datos.get('medico')
        inicio = datos.get('inicio')
        duracion = datos.get('duracion_min')
        if medico and inicio and duracion:
            fin = inicio + timedelta(minutes=duracion)
            posibles = Cita.objects.filter(
                medico=medico, inicio__lt=fin
            ).exclude(estado=Cita.Estado.CANCELADA)
            for otra in posibles:
                if otra.fin > inicio:
                    raise forms.ValidationError(
                        'El médico ya tiene una cita en ese horario '
                        f'({otra.inicio:%d/%m/%Y %H:%M}).'
                    )
        return datos