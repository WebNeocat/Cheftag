from django.db import models
from django.utils import timezone
from app.super.models import ModeloBaseCentro, UserProfile


class RegistroAccion(ModeloBaseCentro):
    usuario = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    accion = models.CharField(max_length=20)  # "crear", "editar", "eliminar"
    modelo = models.CharField(max_length=100)
    objeto_id = models.PositiveIntegerField()
    objeto_repr = models.TextField()
    cambios = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} {self.accion} {self.modelo} ({self.objeto_repr})"


# Create your models here.
