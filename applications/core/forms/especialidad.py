from django import forms
from django.forms import ModelForm
from applications.core.models import Especialidad


class EspecialidadForm(ModelForm):
    class Meta:
        model = Especialidad
        fields = [
            "nombre",
            "descripcion",
            "activo",
        ]
        error_messages = {
            "nombre": {
                "unique": "Ya existe una especialidad médica con este nombre.",
            },
        }
        widgets = {
            "nombre": forms.TextInput(attrs={
                "placeholder": "Ej: Cardiología, Pediatría, Ginecología",
                "id": "id_nombre",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "descripcion": forms.Textarea(attrs={
                "placeholder": "Descripción de la especialidad médica...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
        }
        labels = {
            "nombre": "Especialidad Médica",
            "descripcion": "Descripción",
            "activo": "Activo",
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if nombre:
            # Convertir a formato título (primera letra mayúscula)
            nombre = nombre.strip().title()
            
            # Validar que no esté vacío después del strip
            if not nombre:
                raise forms.ValidationError("El nombre de la especialidad médica no puede estar vacío.")
            
            # Validar longitud mínima
            if len(nombre) < 3:
                raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
                
            return nombre
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if descripcion:
            descripcion = descripcion.strip()
            # Validar longitud mínima si se proporciona descripción
            if descripcion and len(descripcion) < 5:
                raise forms.ValidationError("La descripción debe tener al menos 5 caracteres.")
        return descripcion
