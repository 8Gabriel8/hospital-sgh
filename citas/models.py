from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from pacientes.models import Paciente


class Cita(models.Model):
    class Estado(models.TextChoices):
        SOLICITADA = 'SOLICITADA', 'Solicitada'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        NO_ASISTIO = 'NO_ASISTIO', 'No asistió'

    class Origen(models.TextChoices):
        ADMISION = 'ADMISION', 'Admisión'
        PORTAL = 'PORTAL', 'Portal del paciente'

    TRANSICIONES = {
        'SOLICITADA': ['CONFIRMADA', 'CANCELADA'],
        'CONFIRMADA': ['ATENDIDA', 'NO_ASISTIO', 'CANCELADA'],
        'CANCELADA': [],
        'ATENDIDA': [],
        'NO_ASISTIO': [],
    }

    paciente = models.ForeignKey(
        Paciente, on_delete=models.PROTECT, related_name='citas'
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='citas_como_medico',
    )
    inicio = models.DateTimeField()
    duracion_min = models.PositiveIntegerField(default=30)
    motivo = models.CharField(max_length=200)
    origen = models.CharField(
        max_length=10, choices=Origen.choices, default=Origen.ADMISION
    )
    urgencia_menor = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.SOLICITADA
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['inicio']

    @property
    def fin(self):
        return self.inicio + timedelta(minutes=self.duracion_min)

    def cambiar_estado(self, nuevo):
        if nuevo not in self.TRANSICIONES[self.estado]:
            raise ValidationError(
                f'No se puede pasar de {self.get_estado_display()} a {nuevo}.'
            )
        self.estado = nuevo
        self.save(update_fields=['estado'])

    def __str__(self):
        return f'{self.paciente} - {self.inicio:%d/%m/%Y %H:%M}'