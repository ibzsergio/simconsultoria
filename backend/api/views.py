from django.conf import settings
from django.db import DatabaseError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .mail import enviar_correo_confirmacion_contacto, enviar_notificacion_empresa
from .models import MensajeContacto
from .serializers import MensajeContactoSerializer


def _correo_entrega_fuera_consola() -> bool:
    if getattr(settings, "EMAIL_USE_RESEND", False):
        return True
    backend = (getattr(settings, "EMAIL_BACKEND", "") or "").lower()
    if "console" in backend or "dummy" in backend:
        return False
    if "locmem" in backend or "filebased" in backend:
        return False
    return True


class Salud(APIView):
    def get(self, request):
        return Response({"ok": True, "mensaje": "SIMConsultoria API operativa"}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class ContactoCrear(generics.CreateAPIView):
    queryset = MensajeContacto.objects.all()
    serializer_class = MensajeContactoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except DatabaseError as exc:
            return Response(
                {
                    "detail": (
                        f"Error al guardar en la base de datos: {exc}. "
                        "Comprueba MySQL o ejecuta migrate; en local revisa DJANGO_USE_SQLITE en .env."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        inst = serializer.instance
        try:
            ok_cliente, err_cliente = enviar_correo_confirmacion_contacto(inst)
        except Exception as exc:
            ok_cliente, err_cliente = False, str(exc)
        try:
            ok_empresa, err_empresa = enviar_notificacion_empresa(inst)
        except Exception as exc:
            ok_empresa, err_empresa = False, str(exc)
        any_ok = ok_cliente or ok_empresa
        data = dict(serializer.data)
        data["email_cliente_ok"] = ok_cliente
        data["email_empresa_ok"] = ok_empresa
        data["email_enviado"] = any_ok
        data["email_entrega_real"] = bool(any_ok and _correo_entrega_fuera_consola())
        if err_cliente:
            data["email_error_cliente"] = err_cliente
        if err_empresa:
            data["email_error_empresa"] = err_empresa
        if err_cliente or err_empresa:
            data["email_error"] = err_cliente or err_empresa
        return Response(data, status=status.HTTP_201_CREATED)
