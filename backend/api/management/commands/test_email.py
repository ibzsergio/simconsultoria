from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Envía un correo de prueba por SMTP."

    def add_arguments(self, parser):
        parser.add_argument(
            "destino",
            nargs="?",
            default="",
            help="Correo destino (opcional).",
        )

    def handle(self, *args, **options):
        destino = (options["destino"] or "").strip()
        if not destino:
            destino = (getattr(settings, "CONTACT_NOTIFY_EMAIL", "") or "").strip() or (
                settings.EMAIL_HOST_USER or ""
            ).strip()
        if not destino:
            self.stderr.write(
                "No hay destino. Define CONTACT_NOTIFY_EMAIL o EMAIL_HOST_USER en backend/.env"
            )
            return
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            self.stderr.write(
                "Faltan EMAIL_HOST_USER o EMAIL_HOST_PASSWORD en .env (Gmail: contraseña de aplicación, 16 caracteres)."
            )
            return
        backend = getattr(settings, "EMAIL_BACKEND", "")
        self.stdout.write(f"EMAIL_BACKEND = {backend}")
        self.stdout.write(f"Enviando prueba a: {destino} …")
        try:
            send_mail(
                subject="[SIMConsultoria] Prueba SMTP",
                message="Si recibes esto, Django puede enviar correo correctamente.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destino],
                fail_silently=False,
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Error: {exc}"))
            return
        self.stdout.write(self.style.SUCCESS("Mensaje enviado. Revisa la bandeja (y spam) de: " + destino))
