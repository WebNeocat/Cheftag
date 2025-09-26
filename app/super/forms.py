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
            'fecha_creacion': forms.DateInput (attrs={"class":"form-control form-control-border", "type":"date"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }  


                
class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = UserProfile
        fields = ['centro', 'username', 'password', 'nombre', 'apellidos', 'cargo', 'imagen', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class": "form-control"}),
            'apellidos': forms.TextInput(attrs={"class": "form-control"}),
            'cargo': forms.TextInput(attrs={"class": "form-control"}),
            'estado': forms.CheckboxInput(attrs={"class": "form-check-input"}),
            'centro': forms.Select(attrs={"class": "form-control"}),
        }
        
class CentroUpdateForm(CentroForm):
    class Meta(CentroForm.Meta):
        exclude = ['fecha_creacion']  # o fields sin incluirla        