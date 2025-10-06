from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date
from app.super.models import ModeloBaseCentro
from app.recepcion.models import Proveedor
from app.dashuser.models import Alimento, UnidadDeMedida, Utensilio

class Pedido(ModeloBaseCentro):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_pedido = models.DateField(auto_now_add=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('encamino', 'En camino'),
            ('parcial', 'Parcialmente Recibido'),
            ('recibido', 'Recibido'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente'
    )
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']

    def __str__(self):
        return f"Pedido #{self.id} a {self.proveedor}"

    def total_pedido(self):
        return sum(detalle.total_linea() for detalle in self.detalles.all())
    
    @property
    def cantidad_total_recibida(self):
        """Cantidad total recibida de todos los items del pedido"""
        return sum(d.cantidad_recibida for d in self.detalles.all())
    
    @property
    def porcentaje_recibido(self):
        """Porcentaje del pedido que ha sido recibido"""
        total_pedido = sum(d.cantidad for d in self.detalles.all())
        if total_pedido == 0:
            return 0
        return (self.cantidad_total_recibida / total_pedido) * 100
    
    def actualizar_estado(self):
        """Actualiza el estado del pedido basado en las recepciones"""
        if self.estado == 'cancelado':
            return
        
        total_detalles = self.detalles.count()
        if total_detalles == 0:
            return
        
        detalles_completos = sum(1 for d in self.detalles.all() if d.cantidad_recibida >= d.cantidad)
        
        if detalles_completos == total_detalles:
            self.estado = 'recibido'
            if not self.fecha_entrega:
                self.fecha_entrega = date.today()
        elif self.cantidad_total_recibida > 0:
            self.estado = 'parcial'
        else:
            self.estado = 'encamino' if self.estado != 'pendiente' else 'pendiente'
        
        self.save()


class PedidoDetalle(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    alimento = models.ForeignKey(Alimento, null=True, blank=True, on_delete=models.CASCADE)
    utensilio = models.ForeignKey(Utensilio, null=True, blank=True, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Nuevo campo
    unidad = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def clean(self):
        if not self.alimento_id and not self.utensilio_id:
            raise ValidationError("Debe seleccionar un alimento o un utensilio.")
        if self.alimento_id and self.utensilio_id:
            raise ValidationError("No puede seleccionar ambos: alimento y utensilio.")
        if self.cantidad_recibida > self.cantidad:
            raise ValidationError("La cantidad recibida no puede ser mayor que la cantidad pedida.")

    def total_linea(self):
        return self.cantidad * self.precio_unitario
    
    @property
    def cantidad_por_recibir(self):
        """Cantidad que falta por recibir de este item"""
        return self.cantidad - self.cantidad_recibida
    
    @property
    def porcentaje_recibido(self):
        """Porcentaje recibido de este item específico"""
        if self.cantidad == 0:
            return 0
        return (self.cantidad_recibida / self.cantidad) * 100
    
    def producto(self):
        """Devuelve el producto asociado (alimento o utensilio)"""
        return self.alimento if self.alimento else self.utensilio
    
    def actualizar_cantidad_recibida(self, cantidad):
        """Actualiza la cantidad recibida y ajusta el stock"""
        if cantidad < 0 or (self.cantidad_recibida + cantidad) > self.cantidad:
            raise ValueError("Cantidad recibida no válida")
        
        self.cantidad_recibida += cantidad
        self.save()
        
        # Actualizar el stock del producto
        producto = self.producto()
        if producto:
            producto.stock_actual += cantidad
            producto.save()
        
        # Actualizar estado del pedido padre
        self.pedido.actualizar_estado()

    def __str__(self):
        if self.alimento:
            return f"{self.cantidad} x {self.alimento.nombre} @ {self.precio_unitario}€"
        elif self.utensilio:
            return f"{self.cantidad} x {self.utensilio.nombre} @ {self.precio_unitario}€"
        return f"{self.cantidad} x Item desconocido @ {self.precio_unitario}€"

