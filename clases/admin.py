from django.contrib import admin
from inscripciones.models import Inscripcion
from .models import Clase


class InscripcionInline(admin.TabularInline):
    model = Inscripcion
    extra = 1


@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('pk_cla_id', 'cla_nombre', 'fk_ent', 'cla_dia', 'cla_hora', 'cla_cupo')
    search_fields = ('cla_nombre', 'fk_ent__ent_nombre', 'fk_ent__ent_apellido')
    list_filter = ('cla_dia', 'fk_ent')
    inlines = [InscripcionInline]