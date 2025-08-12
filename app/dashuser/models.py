from django.db import models
from app.super.models import ModeloBaseCentro


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
    
    
class Alimento(ModeloBaseCentro):
    nombre = models.CharField(max_length=100, unique=True)
    nombre_alternativo = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(default='alimentos/default.jpg', upload_to='alimentos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo_alimento = models.ForeignKey(TipoAlimento, on_delete=models.CASCADE, blank=True, null=True)
    conservacion = models.ForeignKey(Conservacion, on_delete=models.CASCADE, blank=True)
    localizacion = models.ForeignKey(localizacion, on_delete=models.CASCADE, blank=True)
    alergenos = models.ManyToManyField(Alergenos, blank=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Alimento"
        verbose_name_plural = 'Alimentos'    
        

    def stock_minimo_format(self):
        return int(self.stock_minimo) if self.stock_minimo % 1 == 0 else self.stock_minimo

    def stock_actual_format(self):
        return int(self.stock_actual) if self.stock_actual % 1 == 0 else self.stock_actual
    
    
class InformacionNutricional(models.Model):
    alimento = models.OneToOneField(Alimento, on_delete=models.CASCADE, related_name="nutricion")
    energia = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    carbohidratos = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    proteinas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    grasas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    azucares = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    sal_mg = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    acido_folico = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    vitamina_c = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    vitamina_a = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    zinc = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    hierro = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    calcio = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    colesterol = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    acidos_grasos_polinsaturados = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    acidos_grasos_monoinsaturados = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    acidos_grasos_saturados = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    fibra = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)

    def __str__(self):
        return f"Información Nutricional de {self.alimento.nombre}"