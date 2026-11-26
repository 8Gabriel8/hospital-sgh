from django.conf import settings
from django.db import models

from pacientes.models import Paciente


class Expediente(models.Model):
    GRUPOS = [
        ('', 'Sin registrar'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    paciente = models.OneToOneField(
        Paciente, on_delete=models.PROTECT, related_name='expediente'
    )
    grupo_sanguineo = models.CharField(max_length=3, choices=GRUPOS, blank=True)
    alergias = models.TextField(blank=True)
    antecedentes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='expedientes_actualizados',
    )

    def __str__(self):
        return f'Expediente de {self.paciente}'


class Consulta(models.Model):
    expediente = models.ForeignKey(
        Expediente, on_delete=models.PROTECT, related_name='consultas'
    )
    cita = models.OneToOneField(
        'citas.Cita',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='consulta',
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='consultas_realizadas',
    )
    fecha_hora = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'Consulta de {self.expediente.paciente} ({self.fecha_hora:%d/%m/%Y})'