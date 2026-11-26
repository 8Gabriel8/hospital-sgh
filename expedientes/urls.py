from django.urls import path

from . import views

app_name = 'expedientes'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:paciente_id>/', views.detalle, name='detalle'),
    path('<int:paciente_id>/consulta/', views.registrar_consulta, name='consulta'),
]