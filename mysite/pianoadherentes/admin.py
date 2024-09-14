from django.contrib import admin
from .models import Titular, Adherente, Log, Plan, DatosUser
# Register your models here.


class TitularAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)

admin.site.register(Titular, TitularAdmin)
admin.site.register(Adherente)
admin.site.register(Log)
admin.site.register(Plan)
admin.site.register(DatosUser)