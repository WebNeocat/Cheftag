from django import forms
from .models import Centros, UserProfile

class CentroForm(forms.ModelForm):
    
    class Meta:
        model = Centros
        fields=['nombre','direccion','ciudad','codigo_postal','pais','telefono','email','sitio_web','fecha_creacion','imagen','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Nombre"}),
            'direccion': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Dirección"}),
            'ciudad': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Ciudad"}),
            'codigo_postal': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Codigo Postal"}),
            'pais': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Pais"}),
            'telefono': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Teléfono"}),
            'email': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Email"}),
            'sitio_web': forms.TextInput(attrs={"class":"form-control form-control-border", "placeholder":"Sitio Web"}),
            'fecha_creacion': forms.DateInput (format=('%Y-%m-%d'), attrs={"class":"form-control form-control-border", "type":"date"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }  


                
class UserProfileForm(forms.ModelForm):

    centro = forms.ModelChoiceField(
        queryset=Centros.objects.none(),  # Inicia vacío
        label="Centro",
        widget=forms.Select(attrs={"class": "form-select form-control-border"}),
        empty_label="Selecciona un centro"
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-border"}),
        min_length=8
    )

    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-border"}),
        min_length=8
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'nombre', 'apellidos', 'cargo', 'imagen', 'centro', 'estado']
        widgets = {
            'username': forms.TextInput(attrs={"class": "form-control form-control-border"}),
            'nombre': forms.TextInput(attrs={"class": "form-control form-control-border"}),
            'apellidos': forms.TextInput(attrs={"class": "form-control form-control-border"}),
            'cargo': forms.TextInput(attrs={"class": "form-control form-control-border"}),
            'imagen': forms.FileInput(attrs={"class": "form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }