from django.contrib import admin
from .models import Titular, Adherente
# Register your models here.


class TitularAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)

admin.site.register(Titular, TitularAdmin)
admin.site.register(Adherente)