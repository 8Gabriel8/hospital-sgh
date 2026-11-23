from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import PacienteForm
from .models import Paciente


def verificar_permiso(user):
    permitido = user.is_superuser or user.groups.filter(name='Admisión').exists()
    if not permitido:
        raise PermissionDenied


@login_required
def lista(request):
    verificar_permiso(request.user)
    pacientes = Paciente.objects.filter(activo=True).order_by('-creado_en')
    return render(request, 'pacientes/lista.html', {'pacientes': pacientes})


@login_required
def registrar(request):
    verificar_permiso(request.user)
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            messages.success(
                request,
                f'Paciente registrado. Expediente: {paciente.numero_expediente}',
            )
            return redirect('pacientes:lista')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/registrar.html', {'form': form})