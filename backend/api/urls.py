from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.Salud.as_view()),
    path("contacto/", views.ContactoCrear.as_view()),
]
