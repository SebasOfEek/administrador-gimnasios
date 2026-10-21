from django.contrib import admin
from membresias.models import Membresia
from .models import Socio


class MembresiaInline(admin.TabularInline):
    model = Membresia
    extra = 1


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('pk_soc_id', 'soc_documento', 'soc_nombre', 'soc_apellido', 'soc_telefono', 'soc_correo')
    search_fields = ('soc_documento', 'soc_nombre', 'soc_apellido', 'soc_correo')
    list_filter = ('soc_apellido',)
    inlines = [MembresiaInline]