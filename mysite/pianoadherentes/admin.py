from django.contrib import admin
from .models import Titular, Adherente, Log, Plan, DatosUser, Sucursales
# Register your models here.


class TitularAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)
    search_fields = ['document', 'last_name', 'name']
    list_display = ('titular_id','name', 'last_name', 'document', 'cbu', 'city', 'is_active', 'created')
    list_filter = ('is_active', 'city', 'province')
    ordering = ['last_name', 'name']


class DatosUserAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'legajo']

class AdherenteAdmin(admin.ModelAdmin):
    search_fields = ['document', 'last_name', 'name', 'legajo']
    list_display = ('adherente_id','name', 'last_name', 'document', 'plan', 'sucursal', 'is_active', 'created')
    list_filter = ('is_active', 'sucursal', 'plan')
    ordering = ['last_name', 'name']



admin.site.register(Titular, TitularAdmin)
admin.site.register(Adherente, AdherenteAdmin)
admin.site.register(Log)
admin.site.register(Plan)
admin.site.register(DatosUser, DatosUserAdmin)
admin.site.register(Sucursales)