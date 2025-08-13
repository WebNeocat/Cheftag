from django import forms
from .models import Plato, AlimentoPlato, TipoPlato

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
    class Meta:
        model = Plato
        fields = ['nombre', 'imagen', 'descripcion','tipoplato']
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

        
    class Meta:
        model = AlimentoPlato
        fields = ['alimento', 'cantidad', 'notas']
        widgets = {
            'alimento': forms.Select(attrs={"class":"form-select form-select-sm form-control-border"}),
            'cantidad': forms.TextInput(attrs={"class":"form-control form-control-sm form-control-border"}),
            'notas': forms.Textarea(attrs={"class":"form-control form-control-sm form-control-border", 'rows': 2}),
        }