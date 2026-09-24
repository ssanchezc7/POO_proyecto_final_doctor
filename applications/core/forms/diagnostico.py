from django import forms
from django.forms import ModelForm
from applications.core.models import Diagnostico


class DiagnosticoForm(ModelForm):
    class Meta:
        model = Diagnostico
        fields = [
            "codigo",
            "descripcion",
            "datos_adicionales",
            "activo",
        ]
        error_messages = {
            "codigo": {
                "unique": "Ya existe un diagnóstico con este código.",
            },
        }
        widgets = {
            "codigo": forms.TextInput(attrs={
                "placeholder": "Ej: A09, J00, K35.2, CIE-10",
                "id": "id_codigo",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "descripcion": forms.TextInput(attrs={
                "placeholder": "Ej: Faringitis aguda, Gastroenteritis viral",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "datos_adicionales": forms.Textarea(attrs={
                "placeholder": "Observaciones clínicas o información adicional...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
        }
        labels = {
            "codigo": "Código del Diagnóstico",
            "descripcion": "Descripción del Diagnóstico",
            "datos_adicionales": "Datos Adicionales",
            "activo": "Activo",
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo")
        if codigo:
            # Convertir a mayúsculas y eliminar espacios extra
            codigo = codigo.strip().upper()
            
            # Validar que no esté vacío después del strip
            if not codigo:
                raise forms.ValidationError("El código del diagnóstico no puede estar vacío.")
            
            # Validar longitud mínima
            if len(codigo) < 2:
                raise forms.ValidationError("El código debe tener al menos 2 caracteres.")
            
            return codigo
        return codigo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if descripcion:
            # Convertir a formato título (primera letra mayúscula)
            descripcion = descripcion.strip().title()
            
            # Validar que no esté vacío después del strip
            if not descripcion:
                raise forms.ValidationError("La descripción del diagnóstico no puede estar vacía.")
            
            # Validar longitud mínima
            if len(descripcion) < 3:
                raise forms.ValidationError("La descripción debe tener al menos 3 caracteres.")
            
            return descripcion
        return descripcion
