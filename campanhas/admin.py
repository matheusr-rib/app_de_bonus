from django.contrib import admin
from .models import Banco, Campanha


class CampanhaAdmin(admin.ModelAdmin):
    list_display = ['campanha', 'banco', 'status_manual', 'vigencia_inicio', 'vigencia_fim']
    list_filter = ['status_manual', 'banco']
    search_fields = ['campanha', 'nomenclatura_wb']
    ordering = ['vigencia_inicio']
    
admin.site.register(Banco)
admin.site.register(Campanha, CampanhaAdmin)