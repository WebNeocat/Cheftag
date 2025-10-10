from django.db import models
from app.super.models import ModeloBaseCentro  
import random
import string
from django.utils import timezone
from datetime import timedelta
from app.dashuser.models import Alimento, UnidadDeMedida, Alergenos


class TextoModo(ModeloBaseCentro):
    nombre = models.CharField(max_length=100)
    texto = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)  # Activo o inactivo

    class Meta:
        verbose_name = "Texto de Modo de Empleo"
        verbose_name_plural = "Textos de Modo de Empleo"

    def __str__(self):
        return self.nombre
    
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
    codigo = models.CharField(blank=True, max_length=10, unique=True, help_text="Código único para el plato")
    texto = models.ForeignKey(TextoModo, on_delete=models.CASCADE, null=True, blank=True)
    vida_util = models.PositiveIntegerField(default=0, help_text="Número de días que se suman a la fecha de producción para calcular la caducidad", null=True, blank=True)
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
    
    def save(self, *args, **kwargs):
        # Si no viene codigo, generarlo automáticamente
        if not self.codigo:
            self.codigo = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        """Genera un código aleatorio de 3 letras único."""
        length = 3  # Longitud del código
        letters = string.ascii_uppercase  # De momento solo letras mayúsculas (17.576 combinaciones)
        code = ''.join(random.choice(letters) for _ in range(length))
        # Comprobar unicidad
        while Plato.objects.filter(codigo=code).exists():
            code = ''.join(random.choice(letters) for _ in range(length))
        return code
    
    @property
    def receta(self):
        """Devuelve la receta asociada a este plato si existe"""
        return self.receta_set.first()  # Usamos first() porque es una ForeignKey
    
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
    
    
    def get_ingredientes_con_info(self):
        """
        Devuelve ingredientes del plato + ingredientes de la salsa (si la tiene)
        con sus alérgenos y trazas.
        """
        ingredientes = []

        # Ingredientes del plato
        for ingrediente in self.ingredientes.all():
            alimento = ingrediente.alimento
            ingredientes.append({
                "nombre": alimento.nombre,
                "alergenos": list(alimento.alergenos.values_list("nombre", flat=True)),
                "trazas": list(alimento.trazas.values_list("nombre", flat=True)),
                "origen": "Plato"
            })

        # Ingredientes de la salsa (si existe)
        if self.salsa:
            for ingrediente in self.salsa.ingredientes.all():
                alimento = ingrediente.alimento
                ingredientes.append({
                    "nombre": alimento.nombre,
                    "alergenos": list(alimento.alergenos.values_list("nombre", flat=True)),
                    "trazas": list(alimento.trazas.values_list("nombre", flat=True)),
                    "origen": f"Salsa: {self.salsa.nombre}"
                })

        return ingredientes
    
    
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
    
    
class EtiquetaPlato(ModeloBaseCentro):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=6, decimal_places=2, help_text="Peso real en gramos")
    fecha = models.DateTimeField(auto_now_add=True)
    caducidad = models.DateField(blank=True, null=True, editable=False)  # NUEVO CAMPO
    lote = models.CharField(max_length=50, blank=True, null=True)

    # Valores nutricionales
    energia = models.DecimalField(max_digits=8, decimal_places=2)
    carbohidratos = models.DecimalField(max_digits=8, decimal_places=2)
    proteinas = models.DecimalField(max_digits=8, decimal_places=2)
    grasas_totales = models.DecimalField(max_digits=8, decimal_places=2)
    azucares = models.DecimalField(max_digits=8, decimal_places=2)
    sal = models.DecimalField(max_digits=8, decimal_places=2)
    grasas_saturadas = models.DecimalField(max_digits=8, decimal_places=2)
    impresa = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Etiqueta de Plato"
        verbose_name_plural = "Etiquetas de Platos"

    def save(self, *args, **kwargs):
        # Asegurarnos de tener fecha completa
        if not self.fecha:
            self.fecha = timezone.now()

        # Generar lote base (sin número) si no existe
        if not self.lote:
            fecha_str = self.fecha.strftime("%d%m%y")
            turno = "A" if self.fecha.hour < 12 else "B"
            codigo_plato = getattr(self.plato, "codigo", self.plato.id)
            lote_base = f"L{fecha_str}-{codigo_plato}-{turno}"

            # Contar cuántos ya existen con este mismo lote base
            ultimo = (
                EtiquetaPlato.objects
                .filter(lote__startswith=lote_base)
                .order_by("-lote")
                .first()
            )

            if ultimo and "-" in ultimo.lote:
                try:
                    secuencia = int(ultimo.lote.split("-")[-1]) + 1
                except ValueError:
                    secuencia = 1
            else:
                secuencia = 1

            # Asignar lote con secuencia formateada a 3 dígitos
            self.lote = f"{lote_base}-{secuencia:03d}"

        # Calcular caducidad si no existe
        if not self.caducidad:
            dias = getattr(self.plato, "vida_util_dias", 3)  # Por defecto 3 días
            self.caducidad = (self.fecha + timedelta(days=dias)).date()  # solo fecha

        super().save(*args, **kwargs)
        
    @property
    def turno(self):
        """Extrae el turno del lote"""
        if self.lote and "-" in self.lote:
            partes = self.lote.split("-")
            if len(partes) >= 3:
                return partes[-2]
        return "A"  # valor por defecto
    
    @property
    def lote_agrupado(self):
        """Devuelve el lote sin los últimos 4 caracteres"""
        if self.lote and len(self.lote) > 4:
            return self.lote[:-4]
        return self.lote


class DatosNuticionales(ModeloBaseCentro):
    plato = models.OneToOneField(Plato, on_delete=models.CASCADE, related_name='nutricion')
    energia = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    grasas_totales = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    grasas_saturadas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    hidratosdecarbono = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    azucares = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    proteinas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    sal = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)

    class Meta:
        verbose_name = "Datos Nutricionales"
        verbose_name_plural = "Datos Nutricionales"

    def __str__(self):
        return f"Datos Nutricionales de {self.plato.nombre}"
    
class NuticionalesSalsa(ModeloBaseCentro):
    salsa = models.OneToOneField(Salsa, on_delete=models.CASCADE, related_name='nutricion')
    energia = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    grasas_totales = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    grasas_saturadas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    hidratosdecarbono = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    azucares = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    proteinas = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)
    sal = models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)

    class Meta:
        verbose_name = "Datos Nutricionales"
        verbose_name_plural = "Datos Nutricionales"

    def __str__(self):
        return f"Datos Nutricionales de {self.salsa.nombre}"    
    
