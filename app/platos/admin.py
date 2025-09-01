from django.contrib import admin
from .models import Receta, AlimentoPlato, Plato, TipoPlato, Salsa, AlimentoSalsa

admin.site.register(AlimentoPlato)
admin.site.register(Receta)
admin.site.register(Plato)
admin.site.register(TipoPlato)
admin.site.register(Salsa)
admin.site.register(AlimentoSalsa)

# Register your models here.
