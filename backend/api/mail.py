import logging
from typing import Optional, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import MensajeContacto

logger = logging.getLogger(__name__)


def _mensaje_error_envio(exc: BaseException) -> str:
    raw = str(exc)
    low = raw.lower()
    if (
        "534" in raw
        or "application-specific password" in low
        or "invalidsecondfactor" in low.replace(" ", "")
    ):
        return (
            "Gmail exige una contraseña de aplicación (16 caracteres), no la contraseña de tu cuenta. "
            "En Google: Cuenta → Seguridad → activa «Verificación en 2 pasos» → "
            "«Contraseñas de aplicaciones» → crea una (p. ej. Correo / Otro) y pega esos 16 caracteres en "
            "EMAIL_HOST_PASSWORD en backend/.env. Reinicia el servidor Django."
        )
    if (
        "535" in raw
        or "username and password not accepted" in low
        or "badcredentials" in low.replace(" ", "")
    ):
        return (
            "Gmail rechazó usuario o contraseña (535). Comprueba: (1) EMAIL_HOST_USER es el correo completo "
            "de la misma cuenta donde creaste la clave, p. ej. nombre@gmail.com; (2) EMAIL_HOST_PASSWORD es la "
            "contraseña de aplicación de 16 letras (no la contraseña con la que entras en el navegador); "
            "(3) sin espacios ni comillas de más en el .env; (4) si la copiaste mal, borra la clave en Google y "
            "genera otra nueva. Guarda .env y reinicia runserver."
        )
    return raw


def _creado_local(instance: MensajeContacto) -> str:
    t = instance.creado
    if timezone.is_aware(t):
        t = timezone.localtime(t)
    return t.strftime("%d/%m/%Y %H:%M")


def _nombre_saludo(nombre_completo: str) -> str:
    partes = (nombre_completo or "").strip().split()
    return partes[0] if partes else "cliente"


def _destino_notificacion_empresa() -> str:
    raw = (getattr(settings, "CONTACT_NOTIFY_EMAIL", None) or "").strip()
    if raw:
        return raw
    return (getattr(settings, "EMAIL_HOST_USER", None) or "").strip()


def enviar_correo_confirmacion_contacto(instance: MensajeContacto) -> Tuple[bool, Optional[str]]:
    marca = getattr(settings, "SIM_MARCA", "SIM")
    ctx = {
        "nombre_saludo": _nombre_saludo(instance.nombre),
        "nombre_completo": instance.nombre,
        "mensaje": instance.mensaje,
        "tema": instance.tema,
        "marca": marca,
    }
    subject = f"Nuevo mensaje desde {marca}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [instance.correo]
    try:
        text_body = render_to_string("emails/confirmacion_contacto.txt", ctx)
        html_body = render_to_string("emails/confirmacion_contacto.html", ctx)
    except Exception as exc:
        logger.exception("Error al renderizar plantilla de correo (cliente)")
        return False, str(exc)
    msg = EmailMultiAlternatives(subject, text_body, from_email, to)
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=False)
        return True, None
    except Exception as exc:
        logger.exception("No se pudo enviar el correo de confirmación a %s", instance.correo)
        return False, _mensaje_error_envio(exc)


def enviar_notificacion_empresa(instance: MensajeContacto) -> Tuple[bool, Optional[str]]:
    destino = _destino_notificacion_empresa()
    if not destino:
        return True, None

    marca = getattr(settings, "SIM_MARCA", "SIM")
    ctx = {
        "marca": marca,
        "nombre": instance.nombre,
        "correo": instance.correo,
        "telefono": instance.telefono or "—",
        "tema": instance.tema,
        "mensaje": instance.mensaje,
        "creado_fmt": _creado_local(instance),
    }
    subject = f"[{marca}] Contacto web: {instance.tema[:60]}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [destino]
    try:
        text_body = render_to_string("emails/notificacion_empresa_contacto.txt", ctx)
        html_body = render_to_string("emails/notificacion_empresa_contacto.html", ctx)
    except Exception as exc:
        logger.exception("Error al renderizar plantilla de correo (empresa)")
        return False, str(exc)
    msg = EmailMultiAlternatives(
        subject,
        text_body,
        from_email,
        to,
        reply_to=[instance.correo],
    )
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=False)
        return True, None
    except Exception as exc:
        logger.exception("No se pudo enviar la notificación al buzón de empresa (%s)", destino)
        return False, _mensaje_error_envio(exc)
