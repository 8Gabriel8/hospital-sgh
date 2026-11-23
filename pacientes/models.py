from django.db import models


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField()
    curp = models.CharField(max_length=18, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    numero_expediente = models.CharField(
        max_length=20, unique=True, null=True, blank=True, editable=False
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.curp = self.curp.upper()
        super().save(*args, **kwargs)
        if not self.numero_expediente:
            self.numero_expediente = f'EXP-{self.pk:05d}'
            super().save(update_fields=['numero_expediente'])

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno} ({self.numero_expediente})'