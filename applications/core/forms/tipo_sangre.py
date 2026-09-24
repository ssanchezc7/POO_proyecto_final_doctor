from django import forms
from django.forms import ModelForm
from applications.core.models import TipoSangre


class TipoSangreForm(ModelForm):
    class Meta:
        model = TipoSangre
        fields = [
            "tipo",
            "descripcion",
        ]
        error_messages = {
            "tipo": {
                "unique": "Ya existe un tipo de sangre con este tipo.",
            },
        }
        widgets = {
            "tipo": forms.TextInput(attrs={
                "placeholder": "Ej: O+, A-, B+, AB-",
                "id": "id_tipo",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "descripcion": forms.Textarea(attrs={
                "placeholder": "Descripción del tipo de sangre...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
        }
        labels = {
            "tipo": "Tipo de Sangre",
            "descripcion": "Descripción",
        }

    def clean_tipo(self):
        tipo = self.cleaned_data.get("tipo")
        if tipo:
            # Validar formato de tipo de sangre
            tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            if tipo.upper() not in tipos_validos:
                raise forms.ValidationError(
                    "Tipo de sangre inválido. Los tipos válidos son: A+, A-, B+, B-, AB+, AB-, O+, O-"
                )
            return tipo.upper()
        return tipo
