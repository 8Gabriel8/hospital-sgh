from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from .forms import CitaForm
from .models import Cita

User = get_user_model()


def es_admision(user):
    return user.is_superuser or user.groups.filter(name='Admisión').exists()


def es_medico(user):
    return user.groups.filter(name='Médico').exists()


@login_required
def agenda(request):
    if not (es_admision(request.user) or es_medico(request.user)):
        raise PermissionDenied

    citas = Cita.objects.select_related('paciente', 'medico')
    medicos = User.objects.filter(
        groups__name='Médico', is_active=True
    ).order_by('first_name', 'username')

    medico_id = ''
    if es_admision(request.user):
        medico_id = request.GET.get('medico', '')
        if medico_id.isdigit():
            citas = citas.filter(medico_id=medico_id)
    else:
        citas = citas.filter(medico=request.user)

    fecha = request.GET.get('fecha', '')
    fecha_valida = parse_date(fecha) if fecha else None
    if fecha_valida:
        citas = citas.filter(inicio__date=fecha_valida)

    contexto = {
        'citas': citas,
        'medicos': medicos,
        'fecha': fecha,
        'medico_id': medico_id,
        'puede_gestionar': es_admision(request.user),
    }
    return render(request, 'citas/agenda.html', contexto)


@login_required
def nueva(request):
    if not es_admision(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.origen = Cita.Origen.ADMISION
            cita.save()
            messages.success(request, 'Cita solicitada correctamente.')
            return redirect('citas:agenda')
    else:
        form = CitaForm()
    return render(request, 'citas/nueva.html', {'form': form})


def _cambiar_estado(request, pk, nuevo, texto_exito):
    if not es_admision(request.user):
        raise PermissionDenied
    cita = get_object_or_404(Cita, pk=pk)
    try:
        cita.cambiar_estado(nuevo)
        messages.success(request, texto_exito)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    return redirect('citas:agenda')


@login_required
@require_POST
def confirmar(request, pk):
    return _cambiar_estado(request, pk, Cita.Estado.CONFIRMADA, 'Cita confirmada.')


@login_required
@require_POST
def cancelar(request, pk):
    return _cambiar_estado(request, pk, Cita.Estado.CANCELADA, 'Cita cancelada.')