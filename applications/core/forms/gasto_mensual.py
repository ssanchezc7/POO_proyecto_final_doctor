from django import forms
from django.forms import ModelForm
from applications.core.models import GastoMensual, TipoGasto


class GastoMensualForm(ModelForm):
    class Meta:
        model = GastoMensual
        fields = [
            "tipo_gasto",
            "fecha",
            "valor",
            "observacion",
        ]
        widgets = {
            "tipo_gasto": forms.Select(attrs={
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "fecha": forms.DateInput(attrs={
                "type": "date",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "valor": forms.NumberInput(attrs={
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "observacion": forms.Textarea(attrs={
                "placeholder": "Observaciones adicionales del gasto...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
        }
        labels = {
            "tipo_gasto": "Tipo de Gasto",
            "fecha": "Fecha del Gasto",
            "valor": "Valor del Gasto ($)",
            "observacion": "Observación",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo tipos de gasto activos
        self.fields['tipo_gasto'].queryset = TipoGasto.objects.filter(activo=True).order_by('nombre')
        
        # Agregar opción vacía para el tipo de gasto
        self.fields['tipo_gasto'].empty_label = "Seleccione un tipo de gasto"

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")
        if valor is not None:
            if valor < 0:
                raise forms.ValidationError("El valor del gasto no puede ser negativo.")
            if valor > 999999.99:
                raise forms.ValidationError("El valor del gasto no puede ser mayor a $999,999.99.")
        return valor

    def clean_observacion(self):
        observacion = self.cleaned_data.get("observacion")
        if observacion:
            observacion = observacion.strip()
            # Validar longitud mínima si se proporciona observación
            if observacion and len(observacion) < 5:
                raise forms.ValidationError("La observación debe tener al menos 5 caracteres.")
        return observacion
