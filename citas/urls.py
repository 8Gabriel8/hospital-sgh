from django.urls import path

from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.agenda, name='agenda'),
    path('nueva/', views.nueva, name='nueva'),
    path('<int:pk>/confirmar/', views.confirmar, name='confirmar'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
]