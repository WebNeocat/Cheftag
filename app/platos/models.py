from django.db import models
from django.db.models import Prefetch
from app.super.models import ModeloBaseCentro   
from app.dashuser.models import Alimento, UnidadDeMedida, Alergenos


class Salsa(ModeloBaseCentro):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='salsas/', null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Salsa'
        verbose_name_plural = 'Salsas'
        unique_together = ('nombre', 'centro')  # Evita nombres duplicados en el mismo centro

    def __str__(self):
        return f"{self.nombre}"
    
    def get_alergenos(self):
        """Devuelve un queryset de alérgenos únicos presentes en la salsa."""
        # Recupera todos los alérgenos asociados a los alimentos de la salsa
        alergenos = Alergenos.objects.filter(
            alimento__alimentosalsa__salsa=self
        ).distinct()
        return alergenos

class AlimentoSalsa(ModeloBaseCentro):
    salsa = models.ForeignKey(Salsa, on_delete=models.CASCADE, related_name='ingredientes')
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE)
    notas = models.TextField(blank=True, null=True)  # Opcional para notas específicas

    class Meta:
        verbose_name = 'Ingrediente de Salsa'
        verbose_name_plural = 'Ingredientes de Salsa'
        unique_together = ('salsa', 'alimento')  # Evita duplicar el mismo alimento en un salsa

    def __str__(self):
        return f"{self.cantidad} {self.unidad_medida.abreviatura} de {self.alimento.nombre} en {self.salsa.nombre}"

    
class TipoPlato(ModeloBaseCentro):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)  # Activo o inactivo

    class Meta:
        verbose_name = 'Tipo de Plato'
        verbose_name_plural = 'Tipos de Platos'
        unique_together = ('nombre', 'centro')  # Evita nombres duplicados en el mismo centro

    def __str__(self):
        return f"{self.nombre}"
    
class Plato(ModeloBaseCentro):
    nombre = models.CharField(max_length=100)
    tipoplato = models.ForeignKey(TipoPlato, on_delete=models.CASCADE, null=True, blank=True)
    imagen = models.ImageField(upload_to='platos/', null=True, blank=True)
    salsa = models.ForeignKey(Salsa, on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Plato'
        verbose_name_plural = 'Platos'
        unique_together = ('nombre', 'centro')  # Evita nombres duplicados en el mismo centro

    def __str__(self):
        return f"{self.nombre}"  
    
    def get_alergenos(self):
        """Devuelve un queryset de alérgenos únicos presentes en el plato y salsa."""
        alergenos_plato = Alergenos.objects.filter(
        alimento__alimentoplato__plato=self
        )

        if self.salsa:
            alergenos_salsa = Alergenos.objects.filter(
                alimento__alimentosalsa__salsa=self.salsa
            )
        else:
            alergenos_salsa = Alergenos.objects.none()

        return (alergenos_plato | alergenos_salsa).distinct()
    
    
class AlimentoPlato(ModeloBaseCentro):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='ingredientes')
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE, blank=True)
    notas = models.TextField(blank=True, null=True)  # Opcional para notas específicas

    class Meta:
        verbose_name = 'Ingrediente de Plato'
        verbose_name_plural = 'Ingredientes de Plato'
        unique_together = ('plato', 'alimento')  # Evita duplicar el mismo alimento en un plato

    def __str__(self):
        return f"{self.cantidad} {self.unidad_medida.abreviatura} de {self.alimento.nombre} en {self.plato.nombre}"
 
    
class Receta(ModeloBaseCentro):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    tiempo_preparacion = models.PositiveIntegerField(verbose_name='Tiempo de preparación (minutos)')
    tiempo_coccion = models.PositiveIntegerField(verbose_name='Tiempo de cocción (minutos)')
    rendimiento = models.PositiveIntegerField(verbose_name='Número de porciones',default=1)
    instrucciones = models.TextField(verbose_name='Instrucciones paso a paso')
    
    class Meta:
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'
        ordering = ['plato__nombre']
    
    def __str__(self):
        return f"{self.plato}"     