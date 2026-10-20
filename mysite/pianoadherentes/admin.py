from django.contrib import admin
from .models import Titular, Adherente, Log, Plan, DatosUser, Sucursales, Movimiento
from .movimientos import guardar_con_movimiento
# Register your models here.


class PersonaAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        guardar_con_movimiento(obj, request.user)


class TitularAdmin(PersonaAdmin):
    readonly_fields = ("created",)
    search_fields = ['document', 'last_name', 'name']
    list_display = ('titular_id','name', 'last_name', 'document', 'cbu', 'city', 'is_active', 'created')
    list_filter = ('is_active', 'city', 'province')
    ordering = ['last_name', 'name']


class DatosUserAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'legajo']

class AdherenteAdmin(PersonaAdmin):
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


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('created', 'tipo_persona', 'nombre', 'movimiento', 'plan_anterior', 'plan_nuevo', 'usuario', 'venta_plus', 'reingreso_plus')
    list_filter = ('tipo_persona', 'movimiento', 'venta_plus', 'reingreso_plus')
    search_fields = ('nombre', 'documento', 'usuario')
    readonly_fields = tuple(field.name for field in Movimiento._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False