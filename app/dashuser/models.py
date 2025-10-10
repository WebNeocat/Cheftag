from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from app.super.models import ModeloBaseCentro
from django.db import transaction



class Alergenos(ModeloBaseCentro):
    nombre = models.CharField('Nombre', max_length=100)
    codigo = models.CharField(max_length=10, blank=True, null=True) 
    imagen = models.ImageField(default='alergenos/default.jpg', upload_to='alergenos/', blank=True, null=True)
    estado = models. BooleanField(default=True)
        
    class Meta:
        verbose_name = 'Alergeno'
        verbose_name_plural = "Alergenos"
        unique_together = ('nombre', 'centro')  # Evitamos duplicados de alérgenos en el mismo centro
        
    def __str__(self):
        return f"{self.nombre}"
    
class Trazas(ModeloBaseCentro):
    nombre = models.CharField('Nombre', max_length=100)
    codigo = models.CharField(max_length=10, blank=True, null=True) 
    imagen = models.ImageField(default='trazas/default.jpg', upload_to='trazas/', blank=True, null=True)
    estado = models. BooleanField(default=True)
        
    class Meta:
        verbose_name = 'Traza'
        verbose_name_plural = "Trazas"
        unique_together = ('nombre', 'centro')  # Evitamos duplicados de alérgenos en el mismo centro
        
    def __str__(self):
        return f"{self.nombre}"    
    

class UnidadDeMedida(ModeloBaseCentro):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "Kilogramo", "Gramo", "Litro"
    abreviatura = models.CharField(max_length=10, unique=True) 
    estado = models. BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        
        
    def __str__(self):
        return f"{self.nombre}"
    
        
class TipoAlimento(ModeloBaseCentro):
    nombre = models.CharField('Nombre', max_length=100)
    estado = models. BooleanField(default=True)
        
    class Meta:
        verbose_name = 'Tipo Alimento'
        verbose_name_plural = 'Tipos de Alimentos'
        
    def __str__(self):
        return f"{self.nombre}"    
    
    
class Conservacion(ModeloBaseCentro):
    nombre = models.CharField('Nombre', max_length=100)
    estado = models. BooleanField(default=True)
        
    class Meta:
        verbose_name = 'Conservación'
        verbose_name_plural = 'Conservaciones'
        
    def __str__(self):
        return f"{self.nombre}"      
    
    
class localizacion  (ModeloBaseCentro):
    localizacion = models.CharField('Localización', max_length=100)
    estado = models. BooleanField(default=True)
     
    class Meta:
        verbose_name = 'Localización'
        verbose_name_plural = 'Localizaciones'
        
    def __str__(self):
        return f"{self.localizacion}"    
    

gtin_validator = RegexValidator(r'^\d{8,14}$', 'El GTIN debe tener entre 8 y 14 dígitos.')
    
class Alimento(ModeloBaseCentro):
    nombre = models.CharField(max_length=100, unique=True)
    nombre_alternativo = models.CharField(max_length=100, blank=True, null=True)
    gtin = models.CharField(max_length=14, blank=True, null=True, help_text="Código GTIN del producto")
    imagen = models.ImageField(default='alimentos/default.jpg', upload_to='alimentos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo_alimento = models.ForeignKey(TipoAlimento, on_delete=models.CASCADE, blank=True, null=True)
    conservacion = models.ForeignKey(Conservacion, on_delete=models.CASCADE, blank=True, null=True)
    localizacion = models.ForeignKey(localizacion, on_delete=models.CASCADE, blank=True, null=True)
    alergenos = models.ManyToManyField(Alergenos, blank=True)
    trazas = models.ManyToManyField(Trazas, blank=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Alimento"
        verbose_name_plural = 'Alimentos'    
        
    def __str__(self):
        return self.nombre 
    
    def stock_minimo_format(self):
        return int(self.stock_minimo) if self.stock_minimo % 1 == 0 else self.stock_minimo

    def stock_actual_format(self):
        return int(self.stock_actual) if self.stock_actual % 1 == 0 else self.stock_actual
    
    # Métodos mejorados para gestión de stock
    def stock_reservado(self, centro=None):
        """
        Calcula el stock reservado en pedidos no completados
        centro: Opcional, filtra por centro específico
        """
        from pedidos.models import PedidoDetalle
        
        filtros = {
            'alimento': self,
            'pedido__estado__in': ['pendiente', 'enviado', 'parcial'],
            'cantidad__gt': models.F('cantidad_recibida')
        }
        
        if centro:
            filtros['pedido__centro'] = centro
            
        detalles = PedidoDetalle.objects.filter(**filtros)
        return sum(d.cantidad - d.cantidad_recibida for d in detalles)
    
    def stock_disponible(self, centro=None):
        """Stock actual menos reservado (puede filtrar por centro)"""
        return self.stock_actual - self.stock_reservado(centro)
    
    def necesita_reposicion(self, centro=None):
        """Indica si el stock disponible está por debajo del mínimo"""
        return self.stock_disponible(centro) < self.stock_minimo
    
    def actualizar_stock(self, cantidad):
        """
        Actualiza el stock físico de forma segura
        cantidad: puede ser positiva (entrada) o negativa (salida)
        """
        with transaction.atomic():
            Alimento.objects.filter(pk=self.pk).update(
                stock_actual=models.F('stock_actual') + cantidad
            )
            self.refresh_from_db(fields=['stock_actual'])
    
    def get_pedidos_pendientes(self, centro=None):
        """
        Devuelve los pedidos no completados para este alimento
        centro: Opcional, filtra por centro específico
        """
        from pedidos.models import PedidoDetalle
        
        filtros = {
            'alimento': self,
            'pedido__estado__in': ['pendiente', 'enviado', 'parcial'],
            'cantidad__gt': models.F('cantidad_recibida')
        }
        
        if centro:
            filtros['pedido__centro'] = centro
            
        return PedidoDetalle.objects.filter(**filtros).select_related('pedido')
    
    def get_ultimo_pedido_pendiente(self, centro=None):
        """
        Devuelve el último pedido pendiente para este alimento
        """
        pedidos = self.get_pedidos_pendientes(centro)
        return pedidos.order_by('-pedido__fecha_pedido').first()
    
    def __str__(self):
        return self.nombre
    
    
    
class InformacionNutricional(models.Model):
    alimento = models.OneToOneField(Alimento, on_delete=models.CASCADE, related_name="nutricion")
    energia = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True, help_text="Energía en Kj por 100g")
    grasas_totales = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True, help_text="Grasas totales en g por 100g")
    grasas_saturadas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True, help_text="Grasas saturadas en g por 100g")
    hidratosdecarbono = models.DecimalField('Hidratos de carbono',default=0, max_digits=6, decimal_places=2, blank=True, help_text="Hidratos de carbono en g por 100g")
    azucares = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True, help_text="Azúcares en g por 100g")
    proteinas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True, help_text="Proteinas en g por 100g")
    sal = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True, help_text="Sal en g por 100g")

    def __str__(self):
        return f"Información Nutricional de {self.alimento.nombre}"
    
    
class EtiquetaAlimento(models.Model):
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE, related_name='etiquetas')
    lote = models.CharField(max_length=50)  # número de lote que tú escribes
    fecha_caducidad = models.DateField()    # la añades tú manualmente
    fecha_apertura = models.DateTimeField(default=timezone.now)  # se completa automáticamente
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Etiqueta {self.alimento.nombre} - Lote {self.lote}"    
    
    
class Utensilio(ModeloBaseCentro):
    nombre = models.CharField(max_length=100, unique=True)  
    gtin = models.CharField(max_length=14, blank=True, null=True, help_text="Código GTIN del producto")
    imagen = models.ImageField(default='utensilios/default.jpg', upload_to='utensilios/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)  # Stock disponible
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Stock mínimo para alerta
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Utensilio'
        verbose_name_plural = 'Utensilios'

    def stock_minimo_format(self):
        return int(self.stock_minimo) if self.stock_minimo % 1 == 0 else self.stock_minimo

    def stock_actual_format(self):
        return int(self.stock_actual) if self.stock_actual % 1 == 0 else self.stock_actual

    
    def stock_disponible(self, centro=None):
        """Stock actual menos reservado (puede filtrar por centro)"""
        return self.stock_actual - self.stock_reservado(centro)
    
    def necesita_reposicion(self, centro=None):
        """Indica si el stock disponible está por debajo del mínimo"""
        return self.stock_disponible(centro) < self.stock_minimo
    
    def actualizar_stock(self, cantidad):
        """
        Actualiza el stock físico de forma segura
        cantidad: puede ser positiva (entrada) o negativa (salida)
        """
        self.stock_actual = models.F('stock_actual') + cantidad
        self.save(update_fields=['stock_actual'])
    
    def get_pedidos_pendientes(self, centro=None):
        """
        Devuelve los pedidos no completados para este utensilio
        centro: Opcional, filtra por centro específico
        """
        from pedidos.models import PedidoDetalle
        
        filtros = {
            'utensilio': self,
            'pedido__estado__in': ['pendiente', 'enviado', 'parcial'],
            'cantidad__gt': models.F('cantidad_recibida')
        }
        
        if centro:
            filtros['pedido__centro'] = centro
            
        return PedidoDetalle.objects.filter(**filtros).select_related('pedido')
    
    def get_ultimo_pedido_pendiente(self, centro=None):
        """
        Devuelve el último pedido pendiente para este utensilio
        """
        pedidos = self.get_pedidos_pendientes(centro)
        return pedidos.order_by('-pedido__fecha_pedido').first()
    
    def __str__(self):
        return f"{self.nombre}"    
  