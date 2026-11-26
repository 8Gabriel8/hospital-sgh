from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from citas.models import Cita
from pacientes.models import Paciente

from .forms import ExpedienteForm
from .models import Expediente


def es_medico(user):
    return user.groups.filter(name='Médico').exists()


def citas_activas_del_medico(user):
    return Cita.objects.filter(medico=user).exclude(estado=Cita.Estado.CANCELADA)


@login_required
def lista(request):
    if not es_medico(request.user):
        raise PermissionDenied
    ids = citas_activas_del_medico(request.user).values_list('paciente_id', flat=True)
    pacientes = Paciente.objects.filter(pk__in=ids, activo=True).order_by(
        'apellido_paterno', 'nombre'
    )
    return render(request, 'expedientes/lista.html', {'pacientes': pacientes})


@login_required
def detalle(request, paciente_id):
    if not es_medico(request.user):
        raise PermissionDenied
    paciente = get_object_or_404(Paciente, pk=paciente_id, activo=True)
    relacion = citas_activas_del_medico(request.user).filter(paciente=paciente).exists()
    if not relacion:
        raise PermissionDenied

    expediente, _ = Expediente.objects.get_or_create(paciente=paciente)

    if request.method == 'POST':
        form = ExpedienteForm(request.POST, instance=expediente)
        if form.is_valid():
            esperada = form.cleaned_data['version_esperada']
            with transaction.atomic():
                actual = Expediente.objects.select_for_update().get(pk=expediente.pk)
                if actual.version != esperada:
                    messages.error(
                        request,
                        'Alguien más actualizó este expediente mientras lo editabas. '
                        'Se muestra la versión vigente; vuelve a aplicar tus cambios.',
                    )
                    return redirect('expedientes:detalle', paciente_id=paciente.pk)
                nuevo = form.save(commit=False)
                nuevo.version = actual.version + 1
                nuevo.actualizado_por = request.user
                nuevo.save()
            messages.success(request, 'Expediente actualizado correctamente.')
            return redirect('expedientes:detalle', paciente_id=paciente.pk)
    else:
        form = ExpedienteForm(
            instance=expediente, initial={'version_esperada': expediente.version}
        )

    contexto = {'paciente': paciente, 'expediente': expediente, 'form': form}
    return render(request, 'expedientes/detalle.html', contexto)