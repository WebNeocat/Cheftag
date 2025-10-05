from django.db import models
from django.contrib.auth.models import User
        

class Centros(models.Model):
    nombre = models.CharField('Nombre', max_length=255, null=False, blank =False) 
    direccion = models.CharField('Dirección', max_length=255, null=True, blank =True)
    ciudad = models.CharField('Ciudad', max_length=100, null=True, blank =True)
    codigo_postal = models.CharField('Codigo Postal', max_length=20, null=True, blank =True)
    pais = models.CharField('Pais', max_length=50, null=True, blank =True)
    telefono = models.CharField('Teléfono', max_length=20, null=True, blank =True)
    email = models.CharField('Email', max_length=255, null=True, blank =True)
    sitio_web = models.CharField('Sitio Web', max_length=20, null=True, blank =True)
    fecha_creacion = models.DateField('Fecha', null=True, blank=True)
    imagen = models.ImageField(default='centro/default.png', upload_to='centros/', null=True, blank =True)
    estado = models. BooleanField(default=True)
    
    
    class Meta:
        verbose_name = 'Centro'
        
    def __str__(self):
        return str(self.nombre)
    

class ModeloBaseCentro(models.Model):
    centro = models.ForeignKey(Centros, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    centro = models.ForeignKey('Centros' ,on_delete=models.CASCADE, null=True, blank =True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(default='users/default.png', upload_to='users/', null=True, blank =True)
    estado =models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.estado:
            Permiso.objects.filter(usuario=self).delete()
            
            
class Permiso(models.Model):
    ACCIONES = [
        ('create', 'Crear'),
        ('read', 'Ver'),
        ('update', 'Editar'),
        ('delete', 'Eliminar'),
    ]

    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='permisos')
    modulo = models.CharField(max_length=100)  # Ejemplo: "Proveedores", "Alérgenos"
    accion = models.CharField(max_length=10, choices=ACCIONES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'modulo', 'accion')
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellidos} → {self.modulo} [{self.accion}]"    