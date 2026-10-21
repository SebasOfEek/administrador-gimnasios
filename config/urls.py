from django.contrib import admin
from django.urls import path

from .views import catalogo, crear_registro, eliminar_registro, inicio

urlpatterns = [
    path('', inicio, name='inicio'),
    path('catalogo/<slug:modulo>/', catalogo, name='catalogo'),
    path('catalogo/<slug:modulo>/crear/', crear_registro, name='crear_registro'),
    path('catalogo/<slug:modulo>/<int:registro_id>/eliminar/', eliminar_registro, name='eliminar_registro'),
    path('admin/', admin.site.urls),
]