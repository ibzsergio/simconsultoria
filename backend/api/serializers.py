from rest_framework import serializers

from .models import MensajeContacto


class MensajeContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeContacto
        fields = ["id", "nombre", "correo", "telefono", "tema", "mensaje", "creado"]
        read_only_fields = ["id", "creado"]
