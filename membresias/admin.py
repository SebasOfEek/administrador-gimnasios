from django.contrib import admin
from .models import Membresia


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = ('pk_mem_id', 'fk_soc', 'fk_pla', 'fk_usu', 'mem_inicio', 'mem_fin')
    search_fields = ('fk_soc__soc_nombre', 'fk_soc__soc_apellido', 'fk_soc__soc_documento')
    list_filter = ('fk_pla', 'mem_inicio')