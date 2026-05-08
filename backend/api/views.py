import logging
import threading

from django.conf import settings
from django.db import DatabaseError, close_old_connections, transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .mail import enviar_correo_confirmacion_contacto, enviar_notificacion_empresa
from .models import MensajeContacto
from .serializers import MensajeContactoSerializer

logger = logging.getLogger(__name__)


def _enviar_correos_contacto_en_fondo(pk: int) -> None:
    close_old_connections()
    try:
        inst = MensajeContacto.objects.get(pk=pk)
    except MensajeContacto.DoesNotExist:
        logger.warning("Contacto %s no existe; no se envían correos.", pk)
        return
    try:
        _ok_c, err_c = enviar_correo_confirmacion_contacto(inst)
        if err_c:
            logger.error("Correo al visitante falló: %s", err_c)
    except Exception:
        logger.exception("Excepción al enviar correo al visitante")
    try:
        _ok_e, err_e = enviar_notificacion_empresa(inst)
        if err_e:
            logger.error("Correo a empresa falló: %s", err_e)
    except Exception:
        logger.exception("Excepción al enviar correo a empresa")
    finally:
        close_old_connections()


def _correo_entrega_fuera_consola() -> bool:
    if getattr(settings, "EMAIL_USE_RESEND", False):
        return True
    if getattr(settings, "EMAIL_USE_SENDGRID", False):
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
        pk = serializer.instance.pk

        def _iniciar_correo_tras_commit() -> None:
            threading.Thread(
                target=_enviar_correos_contacto_en_fondo,
                args=(pk,),
                daemon=True,
            ).start()

        transaction.on_commit(_iniciar_correo_tras_commit)
        data = dict(serializer.data)
        data["email_en_segundo_plano"] = True
        data["email_entrega_real"] = _correo_entrega_fuera_consola()
        return Response(data, status=status.HTTP_201_CREATED)
