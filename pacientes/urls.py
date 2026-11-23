from django.urls import path

from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.registrar, name='registrar'),
]