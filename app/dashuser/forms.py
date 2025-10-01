from django import forms
from .models import Alergenos, Trazas, UnidadDeMedida, TipoAlimento, localizacion, Conservacion, Alimento, InformacionNutricional, EtiquetaAlimento

class AlergenosForm(forms.ModelForm):
    
    class Meta:
        model = Alergenos
        fields=['nombre', 'codigo','estado','imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'codigo': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }
        
class TrazasForm(forms.ModelForm):
    
    class Meta:
        model = Trazas
        fields=['nombre', 'codigo','estado','imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'codigo': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }        
      

class UnidadDeMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadDeMedida
        fields=['nombre', 'abreviatura','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'abreviatura': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }
        
                
class TipoAlimentosForm(forms.ModelForm):
    
    class Meta:
        model = TipoAlimento
        fields=['nombre','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }
        

class LocalizacionForm(forms.ModelForm):
    
    class Meta:
        model = localizacion
        fields=['localizacion','estado']
        widgets = {
            'localizacion': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }        


class ConservacionForm(forms.ModelForm):
    
    class Meta:
        model = Conservacion
        fields=['nombre','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }   

class AlergenosModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj  # retorna el objeto completo, no un string
    
            
class AlimentoForm(forms.ModelForm):
    
    conservacion = forms.ModelChoiceField(
        queryset=Conservacion.objects.all(),
        label="Conservacion",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un tipo"
    )
    
    tipo_alimento = forms.ModelChoiceField(
        queryset=TipoAlimento.objects.all(),
        label="Tipo de Alimento",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un tipo"
    )
    
    localizacion = forms.ModelChoiceField(
        queryset=localizacion.objects.all(),
        label="Localización",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona una localizacion"
    )

    alergenos = AlergenosModelMultipleChoiceField(
        queryset=Alergenos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    trazas = AlergenosModelMultipleChoiceField(
        queryset=Trazas.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    class Meta:
        model = Alimento
        fields = ['nombre', 'nombre_alternativo', 'gtin',  'alergenos', 'trazas','descripcion', 'conservacion', 'localizacion', 'tipo_alimento', 'stock_minimo', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'nombre_alternativo': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'gtin': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border", "placeholder":"Ej: 01234567890123"}),
            'descripcion': forms.Textarea(attrs={"class": "form-control form-control-sm form-control-border", "style": "height: auto; font-size:16px", "rows": 4}),
            'stock_minimo': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-sm form-control-border"}),
        } 
        
class InformacionNutricionalForm(forms.ModelForm):
    class Meta:
        model = InformacionNutricional
        fields = ['energia', 'hidratosdecarbono', 'azucares', 'proteinas', 'grasas_totales', 'grasas_saturadas', 'sal']
        widgets = {
            'energia': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'hidratosdecarbono': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'azucares': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'proteinas': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'grasas_totales': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'grasas_saturadas': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}), 
            'sal': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),                  
        }
        exclude = ['alimento']   
        

class EtiquetaAlimentoForm(forms.ModelForm):
    alimento = forms.ModelChoiceField(
        queryset=Alimento.objects.all(),
        label="Alimento",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un alimento"
    )
    class Meta:
        model = EtiquetaAlimento
        fields = ['alimento', 'lote', 'fecha_caducidad', 'cantidad']
        widgets = {
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date', "class": "form-control form-control-sm form-control-border"}),
            'lote': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'cantidad': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
        }             