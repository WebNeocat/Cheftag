from django import forms
from .models import Proveedor, Recepcion, TipoDeMerma, Merma
from app.dashuser.models import Alimento, UnidadDeMedida

class ProveedorForm(forms.ModelForm):    
    class Meta:
        model = Proveedor
        fields = ['nombre', 'razon_social', 'cif_nif', 'direccion', 'codigo_postal', 'ciudad', 'provincia', 'pais', 'telefono', 'email', 'web', 'persona_contacto', 'telefono_contacto', 'activo', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'razon_social': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'cif_nif': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'direccion': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'codigo_postal': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'ciudad': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'provincia': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'pais': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'telefono': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'email': forms.EmailInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'web': forms.URLInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'persona_contacto': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'telefono_contacto': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'activo': forms.CheckboxInput(attrs={"class":"form-check-input"}),
            'observaciones': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", "rows":3}),               
        }
  
        
class RecepcionForm(forms.ModelForm):
    alimento = forms.ModelChoiceField(
        queryset=Alimento.objects.all(),
        label="Alimento",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un alimento"
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.all(),
        label="Proveedor",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un alimento"
    )
    class Meta:
        model = Recepcion
        fields = ['proveedor', 'alimento', 'lote', 'fecha_caducidad', 'cantidad']
        widgets = {
            'lote': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date', "class": "form-control form-control-sm form-control-border"}),
            'cantidad': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
        }        
 
        
class RecepcionGS1Form(forms.ModelForm):
    class Meta:
        model = Recepcion
        fields = ['proveedor', 'alimento', 'lote', 'fecha_caducidad', 'cantidad']
        widgets = {
            'proveedor': forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
            'alimento': forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
            'lote': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date', "class": "form-control form-control-sm form-control-border"}),
            'cantidad': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
        }        
        

class TipoDeMermaForm(forms.ModelForm):
    class Meta:
        model = TipoDeMerma
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'descripcion': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", "rows":3}),  
            'activo': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }  
        

class MermaForm(forms.ModelForm):
    alimento = forms.ModelChoiceField(
        queryset=Alimento.objects.all(),
        label="Alimento",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un alimento"
    )
    tipo_merma = forms.ModelChoiceField(
        queryset=TipoDeMerma.objects.all(),
        label="Tipo de merma",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un tipo de merma"
    )
    unidad_medida = forms.ModelChoiceField(
        queryset=UnidadDeMedida.objects.all(),
        label="Unidad de medida",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona una medida"
    )
    
    class Meta:
        model = Merma
        fields = ['alimento', 'tipo_merma', 'cantidad', 'unidad_medida', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", "rows":3}),  
            'cantidad': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
        }               