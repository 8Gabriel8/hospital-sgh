from django import forms

from .models import Paciente


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'curp', 'telefono', 'correo',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'

    def clean_curp(self):
        curp = self.cleaned_data['curp'].strip().upper()
        if len(curp) != 18:
            raise forms.ValidationError('La CURP debe tener 18 caracteres.')
        existente = Paciente.objects.filter(curp=curp).first()
        if existente:
            raise forms.ValidationError(
                f'Ya existe un paciente con esa CURP (expediente {existente.numero_expediente}).'
            )
        return curp

    def clean(self):
        datos = super().clean()
        nombre = datos.get('nombre')
        apellido = datos.get('apellido_paterno')
        fecha = datos.get('fecha_nacimiento')
        if nombre and apellido and fecha:
            existente = Paciente.objects.filter(
                nombre__iexact=nombre,
                apellido_paterno__iexact=apellido,
                fecha_nacimiento=fecha,
            ).first()
            if existente:
                raise forms.ValidationError(
                    f'Ya existe un paciente con el mismo nombre y fecha de nacimiento (expediente {existente.numero_expediente}).'
                )
        return datos