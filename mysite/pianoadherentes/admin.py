from django.contrib import admin
from .models import Titular, Adherente, Log, Plan, DatosUser
# Register your models here.


class TitularAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)

class DatosUserAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'legajo']

admin.site.register(Titular, TitularAdmin)
admin.site.register(Adherente)
admin.site.register(Log)
admin.site.register(Plan)
admin.site.register(DatosUser, DatosUserAdmin)