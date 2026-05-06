import json
import logging
import urllib.error
import urllib.request
from email.utils import parseaddr
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
    if "network is unreachable" in low or "errno 101" in low.replace(" ", ""):
        return (
            "No se pudo conectar al servidor SMTP (red inalcanzable). En hosting a veces falla IPv6 o el puerto. "
            "Prueba en Railway: EMAIL_SMTP_FORCE_IPV4=1 y/o EMAIL_PORT=465 con EMAIL_USE_SSL=1 y EMAIL_USE_TLS=0; "
            "o usa un proveedor SMTP de transaccional (SendGrid/Mailgun/Resend)."
        )
    if "timed out" in low or "timeout" in low:
        return (
            "Tiempo de espera agotado al conectar con SMTP. Revisa EMAIL_HOST/EMAIL_PORT en Railway, firewall del "
            "proveedor y baja EMAIL_TIMEOUT si hace falta."
        )
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


def _from_para_resend() -> str:
    rf = getattr(settings, "RESEND_FROM_EMAIL", "") or ""
    rf = rf.strip()
    if rf:
        return rf
    df = (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
    if df and "no-reply@localhost" not in df.lower():
        return df
    return "SIM Consultoría <onboarding@resend.dev>"


def _enviar_resend(
    to: list[str],
    subject: str,
    text_body: str,
    html_body: str,
    reply_to: Optional[list[str]] = None,
) -> Tuple[bool, Optional[str]]:
    api_key = (getattr(settings, "RESEND_API_KEY", None) or "").strip()
    if not api_key:
        return False, "RESEND_API_KEY no configurado"
    from_email = _from_para_resend()
    payload: dict = {
        "from": from_email,
        "to": [t.strip() for t in to if t.strip()],
        "subject": subject,
        "html": html_body,
        "text": text_body,
    }
    if reply_to:
        rt = reply_to[0].strip()
        if rt:
            payload["reply_to"] = rt
    if not payload["to"]:
        return False, "No hay destinatarios válidos"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request("https://api.resend.com/emails", data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            resp.read()
        return True, None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(raw)
            msg = err.get("message", raw)
        except json.JSONDecodeError:
            msg = raw or str(exc)
        return False, f"Resend: {msg}"
    except OSError as exc:
        return False, _mensaje_error_envio(exc)


def _from_nombre_correo(cadena: str) -> tuple[str, str]:
    name, addr = parseaddr((cadena or "").strip())
    return (name.strip(), addr.strip())


def _from_para_sendgrid() -> tuple[str, str]:
    raw = (getattr(settings, "SENDGRID_FROM_EMAIL", None) or "").strip()
    if not raw:
        raw = (getattr(settings, "DEFAULT_FROM_EMAIL", None) or "").strip()
    name, addr = _from_nombre_correo(raw)
    if addr:
        return name, addr
    return "", ""


def _enviar_sendgrid(
    to: list[str],
    subject: str,
    text_body: str,
    html_body: str,
    reply_to: Optional[list[str]] = None,
) -> Tuple[bool, Optional[str]]:
    api_key = (getattr(settings, "SENDGRID_API_KEY", None) or "").strip()
    if not api_key:
        return False, "SENDGRID_API_KEY no configurado"
    from_name, from_addr = _from_para_sendgrid()
    if not from_addr:
        return False, (
            "SENDGRID_FROM_EMAIL o DEFAULT_FROM_EMAIL debe incluir un correo verificado en SendGrid, "
            'p. ej. "SIM Consultoría <notificaciones@tudominio.com>".'
        )
    recipients = [{"email": t.strip()} for t in to if t.strip()]
    if not recipients:
        return False, "No hay destinatarios válidos"
    payload: dict = {
        "personalizations": [{"to": recipients}],
        "from": {"email": from_addr, **({"name": from_name} if from_name else {})},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": text_body},
            {"type": "text/html", "value": html_body},
        ],
    }
    if reply_to and reply_to[0].strip():
        payload["reply_to"] = {"email": reply_to[0].strip()}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request("https://api.sendgrid.com/v3/mail/send", data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            resp.read()
        return True, None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(raw)
            msgs = []
            for e in err.get("errors", []):
                if isinstance(e, dict) and "message" in e:
                    msgs.append(str(e["message"]))
            msg = "; ".join(msgs) if msgs else err.get("message", raw)
        except json.JSONDecodeError:
            msg = raw or str(exc)
        return False, f"SendGrid: {msg}"
    except OSError as exc:
        return False, _mensaje_error_envio(exc)


def _intentar_envio_https(
    *,
    to: list[str],
    subject: str,
    text_body: str,
    html_body: str,
    reply_to: Optional[list[str]] = None,
) -> Optional[Tuple[bool, Optional[str]]]:
    use_re = getattr(settings, "EMAIL_USE_RESEND", False)
    use_sg = getattr(settings, "EMAIL_USE_SENDGRID", False)
    if not use_re and not use_sg:
        return None
    errores: list[str] = []
    if use_re:
        ok, err = _enviar_resend(
            to=to, subject=subject, text_body=text_body, html_body=html_body, reply_to=reply_to
        )
        if ok:
            return True, None
        if err:
            errores.append(str(err))
    if use_sg:
        ok2, err2 = _enviar_sendgrid(
            to=to, subject=subject, text_body=text_body, html_body=html_body, reply_to=reply_to
        )
        if ok2:
            return True, None
        if err2:
            errores.append(str(err2))
    return False, " | ".join(errores) if errores else "No se pudo enviar por API de correo"


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
    http = _intentar_envio_https(to=to, subject=subject, text_body=text_body, html_body=html_body)
    if http is not None:
        return http
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
    http = _intentar_envio_https(
        to=to,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        reply_to=[instance.correo],
    )
    if http is not None:
        return http
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
