from django import forms
from app.super.models import UserProfile
from .models import Pedido, PedidoDetalle
from app.recepcion.models import Proveedor
from app.dashuser.models import Alimento, Utensilio, UnidadDeMedida



class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['proveedor', 'fecha_entrega', 'observaciones', 'estado']
        widgets = {
            'proveedor': forms.Select(attrs={"class": "form-select form-control-border"}),
            'fecha_entrega': forms.DateInput(attrs={"class": "form-control form-control-border", "type": "date"}, format='%Y-%m-%d'),
            'observaciones': forms.Textarea(attrs={"class": "form-control form-control-border", "rows": 3}),
            'estado': forms.Select(attrs={"class": "form-select form-control-border"}),
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar proveedores por centro del usuario
        if self.user:
            try:
                user_profile = UserProfile.objects.get(user=self.user)
                if user_profile.centro:
                    self.fields['proveedor'].queryset = Proveedor.objects.filter(centro=user_profile.centro)
            except UserProfile.DoesNotExist:
                pass
            
            
class PedidoDetalleForm(forms.ModelForm):
    class Meta:
        model = PedidoDetalle
        fields = ['alimento', 'utensilio', 'cantidad', 'unidad', 'precio_unitario']
        widgets = {
            'alimento': forms.Select(attrs={"class": "form-select form-control-border"}),
            'utensilio': forms.Select(attrs={"class": "form-select form-control-border"}),
            'cantidad': forms.NumberInput(attrs={"class": "form-control form-control-border", "step": "0.01"}),
            'unidad': forms.Select(attrs={"class": "form-select form-control-border"}),
            'precio_unitario': forms.NumberInput(attrs={"class": "form-control form-control-border", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            centro = UserProfile.objects.get(user=user).centro
            if 'alimento' in self.fields:
                self.fields['alimento'].queryset = Alimento.objects.filter(centro=centro)
            if 'utensilio' in self.fields:  # ✅ evita KeyError
                self.fields['utensilio'].queryset = Utensilio.objects.filter(centro=centro)
            if 'unidad' in self.fields:
                self.fields['unidad'].queryset = UnidadDeMedida.objects.filter(centro=centro)

            
            
class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(
        label="Confirma tu contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )                   