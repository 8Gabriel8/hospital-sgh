from django.contrib import admin
from django.urls import include, path

from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.inicio, name='inicio'),
]