from django.contrib import admin
from .models import Entrenador


@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
    list_display = ('pk_ent_id', 'ent_nombre', 'ent_apellido', 'ent_telefono', 'ent_especialidad')
    search_fields = ('ent_nombre', 'ent_apellido', 'ent_especialidad')
    list_filter = ('ent_especialidad',)