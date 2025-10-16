from django import forms
from .models import Alergenos, Trazas, UnidadDeMedida, TipoAlimento, Localizacion, Conservacion, Alimento, InformacionNutricional, EtiquetaAlimento, Utensilio

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
        model = Localizacion
        fields=['nombre','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
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
        queryset=Conservacion.objects.none(),  # ✅ se define vacío y luego se filtra en __init__
        label="Conservación",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un tipo",
        required=False
    )
    
    tipo_alimento = forms.ModelChoiceField(
        queryset=TipoAlimento.objects.none(),
        label="Tipo de Alimento",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un tipo",
        required=False
    )
    
    localizacion = forms.ModelChoiceField(
        queryset=Localizacion.objects.none(),
        label="Localización",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona una localización",
        required=False
    )

    alergenos = AlergenosModelMultipleChoiceField(
        queryset=Alergenos.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    trazas = AlergenosModelMultipleChoiceField(
        queryset=Trazas.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Alimento
        fields = [
            'nombre', 'nombre_alternativo', 'gtin', 'alergenos', 'trazas',
            'descripcion', 'conservacion', 'localizacion', 'tipo_alimento',
            'stock_minimo', 'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'nombre_alternativo': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'gtin': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border", "placeholder":"Ej: 01234567890123"}),
            'descripcion': forms.Textarea(attrs={"class": "form-control form-control-sm form-control-border", "style": "height: auto; font-size:16px", "rows": 4}),
            'stock_minimo': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-sm form-control-border"}),
        } 
        
    def __init__(self, *args, **kwargs):
        centro = kwargs.pop("centro", None)  # ✅ recibimos el centro desde la vista
        super().__init__(*args, **kwargs)

        # Poner todos los campos como opcionales excepto 'nombre'
        for field_name, field in self.fields.items():
            if field_name != 'nombre':
                field.required = False   

        # ✅ Si hay centro, filtramos los queryset
        if centro:
            self.fields['conservacion'].queryset = Conservacion.objects.filter(centro=centro)
            self.fields['tipo_alimento'].queryset = TipoAlimento.objects.filter(centro=centro)
            self.fields['localizacion'].queryset = Localizacion.objects.filter(centro=centro)
            self.fields['alergenos'].queryset = Alergenos.objects.filter(centro=centro)
            self.fields['trazas'].queryset = Trazas.objects.filter(centro=centro)
 
  
        
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
        

class UtensilioForm(forms.ModelForm):
    
    class Meta:
        model = Utensilio
        fields = ['nombre','precio', 'gtin', 'descripcion', 'stock_actual', 'stock_minimo', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'gtin': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'descripcion': forms.Textarea(attrs={"class": "form-control form-control-sm form-control-border", "style": "height: auto; font-size:16px", "rows": 4}),
            'precio': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'stock_actual': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'stock_minimo': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-sm form-control-border"}),
        }
        
        
class EtiquetaAlimentoForm(forms.ModelForm):
    alimento = forms.ModelChoiceField(
        queryset=Alimento.objects.none(),  # se rellenará en __init__
        label="Alimento",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un alimento"
    )

    class Meta:
        model = EtiquetaAlimento
        fields = ['alimento', 'lote', 'fecha_caducidad', 'cantidad']
        widgets = {
            'fecha_caducidad': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', "class": "form-control form-control-sm form-control-border"}
            ),
            'lote': forms.TextInput(attrs={"class": "form-control form-control-sm form-control-border"}),
            'cantidad': forms.NumberInput(attrs={"class": "form-control form-control-sm form-control-border"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filtrar alimentos por el centro del usuario
        if user and hasattr(user, 'userprofile') and user.userprofile.centro:
            self.fields['alimento'].queryset = Alimento.objects.filter(centro=user.userprofile.centro)
        self.fields['fecha_caducidad'].input_formats = ['%Y-%m-%d']
           