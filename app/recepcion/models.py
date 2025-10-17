from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from app.dashuser.models import Alimento, UnidadDeMedida
from app.super.models import ModeloBaseCentro, UserProfile


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
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='recepciones', blank=True)
    alimento = models.ForeignKey(Alimento, on_delete=models.PROTECT, related_name='recepciones')
    lote = models.CharField(max_length=50, help_text="Número de lote del proveedor")
    fecha_caducidad = models.DateField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cantidad recibida (kg, L, etc.)")
    unidad_compra = models.ForeignKey(UnidadDeMedida, on_delete=models.PROTECT, help_text="Unidad de medida (kg, L, etc.)")
    precio_compra = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Precio compra" )
    observaciones = models.TextField(blank=True, null=True)
    fecha_recepcion = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-fecha_recepcion']
        verbose_name = "Recepción"
        verbose_name_plural = "Recepciones"

    def __str__(self):
        return f"{self.alimento.nombre} - {self.lote} ({self.proveedor.nombre})"

    def actualizar_stock_alimento(self):
        alimento = self.alimento
        cantidad_entrada = self.cantidad

        # 1️⃣ Conversión si unidad_compra != unidad_uso
        if alimento.unidad_compra_id != alimento.unidad_uso_id:
            if alimento.peso_unitario and alimento.peso_unitario > 0:
                cantidad_entrada *= alimento.peso_unitario
            else:
                raise ValueError(
                    f"El alimento '{alimento.nombre}' necesita peso_unitario para convertir entre unidades."
                )

        # 2️⃣ Actualizar stock
        with transaction.atomic():
            # Guardamos stock_actual
            Alimento.objects.filter(pk=alimento.pk).update(
                stock_actual=models.F('stock_actual') + cantidad_entrada
            )
            alimento.refresh_from_db(fields=['stock_actual'])

            # Recalculamos stock_util
            alimento.stock_util = alimento.stock_actual * (alimento.porcentaje_uso / 100)

            # 3️⃣ Actualizar precio_medio
            if not alimento.precio_medio or alimento.precio_medio == 0:
                alimento.precio_medio = self.precio_compra
            else:
                # Media ponderada: (stock_antiguo * precio_medio + cantidad_nueva * precio_compra) / stock_total
                stock_antiguo = alimento.stock_actual - cantidad_entrada
                alimento.precio_medio = (
                    (stock_antiguo * alimento.precio_medio) + (cantidad_entrada * self.precio_compra)
                ) / alimento.stock_actual

            # Guardamos cambios finales
            alimento.save(update_fields=['stock_util', 'precio_medio'])

    
    
class TipoDeMerma(ModeloBaseCentro):
    nombre = models.CharField(max_length=100, verbose_name="Tipo de merma")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")  # Para activar/desactivar tipos de merma


    class Meta:
        verbose_name = "Tipo de merma"
        verbose_name_plural = "Tipos de mermas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre    
    
    
class Merma(ModeloBaseCentro):
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE, related_name="mermas")
    tipo_merma = models.ForeignKey(TipoDeMerma, on_delete=models.PROTECT, verbose_name="Tipo de merma")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad perdida")
    unidad_medida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE, verbose_name="Unidad de medida")  # o gr, lt, unidades...
    fecha = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="mermas_registradas")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Merma"
        verbose_name_plural = "Mermas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.alimento.nombre} - {self.cantidad} {self.unidad_medida} ({self.tipo_merma})"

    def save(self, *args, **kwargs):
        # Si la merma ya existía, calculamos diferencia
        if self.pk:  
            old_merma = Merma.objects.get(pk=self.pk)
            diferencia = self.cantidad - old_merma.cantidad
        else:
            diferencia = self.cantidad  # Nueva merma → resta la cantidad entera

        super().save(*args, **kwargs)

        # Actualizar stock en base a diferencia
        if diferencia > 0:  # se perdió más cantidad
            self.alimento.stock_actual = max(self.alimento.stock_actual - diferencia, 0)
        elif diferencia < 0:  # se corrigió a menos pérdida → devolvemos stock
            self.alimento.stock_actual += abs(diferencia)

        self.alimento.save()   
        
        
    def eliminar_y_devolver_stock(self):
        """
        Devuelve la cantidad de la merma al stock del alimento
        y elimina la merma de la base de datos.
        """
        with transaction.atomic():
            # actualizar stock atómicamente
            self.alimento.__class__.objects.filter(pk=self.alimento.pk).update(
                stock_actual=F('stock_actual') + self.cantidad
            )
            # borrar la merma
            self.delete()    
            
            
            
            
class AjusteInventario(ModeloBaseCentro):
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    stock_sistema = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    stock_real = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'

    def __str__(self):
        return f"{self.alimento.nombre} ({self.fecha.date()} - {self.centro})"
        