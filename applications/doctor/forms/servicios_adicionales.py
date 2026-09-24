from django import forms
from django.forms import ModelForm
from applications.doctor.models import ServiciosAdicionales


class ServiciosAdicionalesForm(ModelForm):
    class Meta:
        model = ServiciosAdicionales
        fields = [
            "nombre_servicio",
            "descripcion",
            "costo_servicio",
            "activo",
        ]
        error_messages = {
            "nombre_servicio": {
                "unique": "Ya existe un servicio adicional con este nombre.",
            },
        }
        widgets = {
            "nombre_servicio": forms.TextInput(attrs={
                "placeholder": "Ej: Radiografía, Laboratorio clínico, Procedimiento menor",
                "id": "id_nombre_servicio",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "descripcion": forms.Textarea(attrs={
                "placeholder": "Descripción del servicio adicional...",
                "id": "id_descripcion",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                "rows": 3,
            }),
            "costo_servicio": forms.NumberInput(attrs={
                "placeholder": "Ej: 25.00",
                "id": "id_costo_servicio",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                "step": "0.01",
                "min": "0",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-500",
                "id": "id_activo",
            }),
        }

    def clean_nombre_servicio(self):
        nombre_servicio = self.cleaned_data.get('nombre_servicio')
        if nombre_servicio:
            nombre_servicio = nombre_servicio.strip().title()
            if len(nombre_servicio) < 3:
                raise forms.ValidationError("El nombre del servicio debe tener al menos 3 caracteres.")
            if len(nombre_servicio) > 255:
                raise forms.ValidationError("El nombre del servicio no puede tener más de 255 caracteres.")
        return nombre_servicio

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion:
            descripcion = descripcion.strip()
            if len(descripcion) > 1000:
                raise forms.ValidationError("La descripción no puede tener más de 1000 caracteres.")
        return descripcion

    def clean_costo_servicio(self):
        costo_servicio = self.cleaned_data.get('costo_servicio')
        if costo_servicio is not None:
            if costo_servicio < 0:
                raise forms.ValidationError("El costo del servicio no puede ser negativo.")
            if costo_servicio > 99999999.99:
                raise forms.ValidationError("El costo del servicio no puede exceder $99,999,999.99.")
        return costo_servicio
