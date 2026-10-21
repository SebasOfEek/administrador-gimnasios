from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('pk_usu_id', 'usu_usuario', 'usu_nombre', 'usu_apellido', 'usu_correo', 'usu_rol')
    search_fields = ('usu_usuario', 'usu_nombre', 'usu_apellido', 'usu_correo')
    list_filter = ('usu_rol',)