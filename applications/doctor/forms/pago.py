from django import forms
from django.forms import ModelForm
from decimal import Decimal
from applications.doctor.models import Pago, DetallePago, ServiciosAdicionales
from applications.doctor.utils.pago import MetodoPagoChoices, EstadoPagoChoices





class DetallePagoForm(ModelForm):
    class Meta:
        model = DetallePago
        fields = [
            'servicio_adicional',
            'cantidad',
            'precio_unitario',
            'descuento_porcentaje',
            'aplica_seguro',
            'valor_seguro',
            'descripcion_seguro'
        ]
        widgets = {
            'servicio_adicional': forms.Select(attrs={
                'class': 'form-select',
            }),
            'cantidad': forms.NumberInput(attrs={
                'placeholder': '1',
                'min': '1',
                'class': 'form-control',
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'form-control',
            }),
            'descuento_porcentaje': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'class': 'form-control',
            }),
            'aplica_seguro': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'valor_seguro': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'form-control',
            }),
            'descripcion_seguro': forms.TextInput(attrs={
                'placeholder': 'Nombre del seguro utilizado',
                'class': 'form-control',
            }),
        }
        labels = {
            'servicio_adicional': 'Servicio',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario ($)',
            'descuento_porcentaje': 'Descuento (%)',
            'aplica_seguro': 'Aplica Seguro',
            'valor_seguro': 'Valor Cubierto por Seguro ($)',
            'descripcion_seguro': 'Descripción del Seguro',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo servicios activos
        self.fields['servicio_adicional'].queryset = ServiciosAdicionales.objects.filter(activo=True).order_by('nombre_servicio')
        self.fields['servicio_adicional'].empty_label = "Seleccione un servicio"

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_descuento_porcentaje(self):
        descuento = self.cleaned_data.get('descuento_porcentaje')
        if descuento and (descuento < 0 or descuento > 100):
            raise forms.ValidationError("El descuento debe estar entre 0 y 100%.")
        return descuento


class PagoPayPalForm(forms.Form):
    """
    Formulario para procesar pagos con PayPal
    """
    pago_id = forms.IntegerField(widget=forms.HiddenInput())
    monto = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.HiddenInput()
    )
    descripcion = forms.CharField(
        max_length=255,
        widget=forms.HiddenInput()
    )
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0.")
        return monto


class BuscarPagoForm(forms.Form):
    """
    Formulario para buscar pagos
    """
    ESTADO_CHOICES = [('', 'Todos los estados')] + list(EstadoPagoChoices.choices)
    METODO_CHOICES = [('', 'Todos los métodos')] + list(MetodoPagoChoices.choices)
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por paciente, referencia...',
            'class': 'form-control',
        }),
        label='Buscar'
    )
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Estado'
    )
    
    metodo_pago = forms.ChoiceField(
        choices=METODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Método de Pago'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Hasta'
    )


class PagoSearchForm(forms.Form):
    """Formulario para buscar pagos"""
    
    paciente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del paciente...'
        }),
        label='Paciente'
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + EstadoPagoChoices.choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Estado'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Hasta'
    )


class PayPalPaymentForm(forms.Form):
    """Formulario para procesar pagos con PayPal"""
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )


class PagoStatusUpdateForm(forms.ModelForm):
    """Formulario para actualizar el estado de un pago"""
    
    class Meta:
        model = Pago
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'form-select'
            })
        }
