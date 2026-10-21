from django.contrib import admin
from .models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('pk_pla_id', 'pla_nombre', 'pla_precio', 'pla_dias')
    search_fields = ('pla_nombre',)
    list_filter = ('pla_dias',)