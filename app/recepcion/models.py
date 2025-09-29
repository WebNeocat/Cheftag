from django.db import models
from django.utils import timezone
from app.dashuser.models import Alimento
from app.super.models import ModeloBaseCentro

class Proveedor(ModeloBaseCentro):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre comercial")
    razon_social = models.CharField(max_length=200, blank=True, verbose_name="Razón social")
    cif_nif = models.CharField(max_length=20, blank=True, verbose_name="CIF/NIF")
    direccion = models.CharField(max_length=255, null=True,blank=True, verbose_name="Dirección")
    codigo_postal = models.CharField(max_length=10, blank=True, null=True,verbose_name="Código postal")
    ciudad = models.CharField(max_length=100, blank=True, null=True,verbose_name="Ciudad")
    provincia = models.CharField(max_length=100, blank=True, null=True,verbose_name="Provincia")
    pais = models.CharField(max_length=100, default="España", null=True,verbose_name="País")
    telefono = models.CharField(max_length=50, blank=True, null=True,verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True,verbose_name="Correo electrónico")
    web = models.URLField(blank=True, null=True,verbose_name="Sitio web")
    persona_contacto = models.CharField(max_length=150, blank=True, null=True,verbose_name="Persona de contacto")
    telefono_contacto = models.CharField(max_length=50, blank=True, null=True,verbose_name="Teléfono de contacto")
    activo = models.BooleanField(default=True, null=True,verbose_name="Proveedor activo")
    fecha_alta = models.DateField(auto_now_add=True, verbose_name="Fecha de alta")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    class Meta:
        ordering = ['nombre']
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


class Recepcion(ModeloBaseCentro):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='recepciones')
    alimento = models.ForeignKey(Alimento, on_delete=models.PROTECT, related_name='recepciones')
    lote = models.CharField(max_length=50, help_text="Número de lote del proveedor")
    fecha_caducidad = models.DateField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cantidad recibida (kg, L, etc.)")
    fecha_recepcion = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-fecha_recepcion']
        verbose_name = "Recepción"
        verbose_name_plural = "Recepciones"

    def __str__(self):
        return f"{self.alimento.nombre} - {self.lote} ({self.proveedor.nombre})"