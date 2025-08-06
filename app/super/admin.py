from django.contrib import admin
from .models import UserProfile, Centros
# Register your models here.

admin.site.register(Centros)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre', 'centro', 'estado')
    list_filter = ('centro', 'estado')
    search_fields = ('username', 'nombre', 'apellidos')