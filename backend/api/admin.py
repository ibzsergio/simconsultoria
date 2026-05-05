from django.contrib import admin

from .models import MensajeContacto


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "correo", "tema", "creado")
    search_fields = ("nombre", "correo", "tema")
    readonly_fields = ("creado",)
