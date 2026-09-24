from django import forms
from django.forms import ModelForm
from applications.core.models import Medicamento, TipoMedicamento, MarcaMedicamento
from applications.core.utils.medicamento import ViaAdministracion


class MedicamentoForm(ModelForm):
    class Meta:
        model = Medicamento
        fields = [
            "nombre",
            "descripcion",
            "concentracion",
            "via_administracion",
            "tipo",
            "marca_medicamento",
            "cantidad",
            "precio",
            "comercial",
            "foto",
            "activo",
        ]
        error_messages = {
            "nombre": {
                "unique": "Ya existe un medicamento con este nombre.",
            },
        }
        widgets = {
            "nombre": forms.TextInput(attrs={
                "placeholder": "Ej: Ibuprofeno, Paracetamol, Amoxicilina",
                "id": "id_nombre",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "descripcion": forms.Textarea(attrs={
                "placeholder": "Descripción del medicamento, indicaciones, contraindicaciones...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "concentracion": forms.TextInput(attrs={
                "placeholder": "Ej: 500mg, 1g, 5%, 250mg/5ml",
                "id": "id_concentracion",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "via_administracion": forms.Select(attrs={
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "tipo": forms.Select(attrs={
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "marca_medicamento": forms.Select(attrs={
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "cantidad": forms.NumberInput(attrs={
                "placeholder": "Ej: 100",
                "min": "0",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "precio": forms.NumberInput(attrs={
                "placeholder": "Ej: 15.50",
                "min": "0",
                "step": "0.01",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "comercial": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
            "foto": forms.ClearableFileInput(attrs={
                "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-gray-700 dark:file:text-gray-300 dark:text-gray-400",
                "accept": "image/*",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
        }
        labels = {
            "nombre": "Nombre del Medicamento",
            "descripcion": "Descripción",
            "concentracion": "Concentración",
            "via_administracion": "Vía de Administración",
            "tipo": "Tipo de Medicamento",
            "marca_medicamento": "Marca",
            "cantidad": "Stock Disponible",
            "precio": "Precio ($)",
            "comercial": "Medicamento Comercial",
            "foto": "Imagen del Medicamento",
            "activo": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo tipos y marcas activos
        self.fields['tipo'].queryset = TipoMedicamento.objects.filter(activo=True)
        self.fields['marca_medicamento'].queryset = MarcaMedicamento.objects.filter(activo=True)
        
        # Agregar opción vacía para marca (es opcional)
        self.fields['marca_medicamento'].empty_label = "Seleccionar marca (opcional)"

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if nombre:
            # Convertir a formato título (primera letra mayúscula)
            nombre = nombre.strip().title()
            
            # Validar que no esté vacío después del strip
            if not nombre:
                raise forms.ValidationError("El nombre del medicamento no puede estar vacío.")
            
            # Validar longitud mínima
            if len(nombre) < 2:
                raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
                
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

    def clean_concentracion(self):
        concentracion = self.cleaned_data.get("concentracion")
        if concentracion:
            concentracion = concentracion.strip()
            # Validar longitud mínima si se proporciona concentración
            if concentracion and len(concentracion) < 2:
                raise forms.ValidationError("La concentración debe tener al menos 2 caracteres.")
        return concentracion

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad")
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError("La cantidad no puede ser negativa.")
        return cantidad

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio
