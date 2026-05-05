from django.db import models


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=120)
    correo = models.EmailField()
    telefono = models.CharField(max_length=40, blank=True)
    tema = models.CharField(max_length=200)
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self) -> str:
        return f"{self.nombre} — {self.tema}"
