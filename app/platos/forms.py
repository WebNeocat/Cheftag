from django import forms
from .models import Plato, AlimentoPlato, TipoPlato, Salsa, AlimentoSalsa

class SalsaForm(forms.ModelForm):    
    class Meta:
        model = Salsa
        fields = ['nombre', 'imagen', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'descripcion': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", 'rows': 3}),
        }


class AlimentoSalsaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar el campo alimento por nombre
        self.fields['alimento'].queryset = self.fields['alimento'].queryset.order_by('nombre')
        # Ordenar el campo unidad_medida por nombre
        self.fields['unidad_medida'].queryset = self.fields['unidad_medida'].queryset.order_by('nombre')
        
    class Meta:
        model = AlimentoSalsa
        fields = ['alimento', 'cantidad', 'unidad_medida', 'notas']
        widgets = {
            'alimento': forms.Select(attrs={"class":"form-select form-select-sm form-control-border"}),
            'cantidad': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'unidad_medida': forms.Select(attrs={"class":"form-select form-select-sm form-control-border"}),
            'notas': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", 'rows': 5}),
        }

# Formset para los ingredientes
AlimentoSalsaFormSet = forms.inlineformset_factory(
    Salsa, 
    AlimentoSalsa, 
    form=AlimentoSalsaForm,
    extra=1,
    can_delete=True
)

class TipoPlatoForm(forms.ModelForm):
    
    class Meta:
        model = TipoPlato
        fields=['nombre', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-border"}),
            'estado': forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }


class PlatoForm(forms.ModelForm):
    tipoplato = forms.ModelChoiceField(
        queryset=TipoPlato.objects.all(),
        label="Tipo de Plato",
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona un tipo"
    )
    salsa = forms.ModelChoiceField(
        queryset=Salsa.objects.all(),
        label="Salsa",
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm form-control-border"}),
        empty_label="Selecciona una salsa"
    )
    class Meta:
        model = Plato
        fields = ['nombre', 'imagen', 'descripcion', 'salsa', 'tipoplato']
        widgets = {
            'nombre': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'imagen': forms.FileInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'descripcion': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", 'rows': 3}),
        }

class AlimentoPlatoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar el campo alimento por nombre
        self.fields['alimento'].queryset = self.fields['alimento'].queryset.order_by('nombre')
        # Ordenar el campo unidad_medida por nombre
        self.fields['unidad_medida'].queryset = self.fields['unidad_medida'].queryset.order_by('nombre')
        
    class Meta:
        model = AlimentoPlato
        fields = ['alimento', 'cantidad', 'unidad_medida', 'notas']
        widgets = {
            'alimento': forms.Select(attrs={"class":"form-select form-select-sm form-control-border"}),
            'cantidad': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'unidad_medida': forms.Select(attrs={"class":"form-select form-select-sm form-control-border"}),
            'notas': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", 'rows': 2}),
        }

# Formset para los ingredientes
AlimentoPlatoFormSet = forms.inlineformset_factory(
    Plato, 
    AlimentoPlato, 
    form=AlimentoPlatoForm,
    extra=1,
    can_delete=True
)        