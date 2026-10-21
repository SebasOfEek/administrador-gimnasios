from django.contrib import admin
from .models import Inscripcion


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('pk_inc_id', 'fk_soc', 'fk_cla', 'fk_usu', 'inc_fecha')
    search_fields = ('fk_soc__soc_nombre', 'fk_soc__soc_apellido', 'fk_cla__cla_nombre')
    list_filter = ('inc_fecha', 'fk_cla')