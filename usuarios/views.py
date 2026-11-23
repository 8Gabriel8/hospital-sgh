from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inicio(request):
    grupos = request.user.groups.values_list('name', flat=True)
    return render(request, 'inicio.html', {'grupos': grupos})