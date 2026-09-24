import re
from django import forms
from django.forms import ModelForm
from applications.security.models import Module, Menu

class ModuleForm(ModelForm):
    class Meta:
        model = Module
        fields = [
            "name",
            "url", 
            "menu",
            "description",
            "icon",
            "order",
            "is_active",
            "permissions",
        ]
        error_messages = {
            "url": {
                "unique": "Ya existe un módulo con esta URL.",
            },
            "name": {
                "unique": "Ya existe un módulo con este nombre.",
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ingrese nombre del módulo",
                "id": "id_name",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "url": forms.TextInput(attrs={
                "placeholder": "Ej: security:module_list",
                "id": "id_url",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "menu": forms.Select(attrs={
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Descripción detallada del módulo...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "icon": forms.TextInput(attrs={
                "placeholder": "Ej: fas fa-users",
                "id": "id_icon",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 font-mono text-sm",
            }),
            "order": forms.NumberInput(attrs={
                "placeholder": "1",
                "id": "id_order",
                "min": "1",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
            "permissions": forms.CheckboxSelectMultiple(attrs={
                "class": "space-y-2",
            }),
        }
        labels = {
            "name": "Nombre",
            "url": "URL",
            "menu": "Menú",
            "description": "Descripción",
            "icon": "Ícono",
            "order": "Orden",
            "is_active": "Activo",
            "permissions": "Permisos",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo de menu use las opciones de la base de datos
        if hasattr(Menu, 'objects'):
            self.fields['menu'].queryset = Menu.objects.all()

    def clean_name(self):
        name = self.cleaned_data.get("name")
        return name.upper() if name else name
    
    def clean_icon(self):
        icon = self.cleaned_data.get('icon')
        if not icon:
            raise forms.ValidationError("El campo ícono es requerido.")
        
        # Patrones para FontAwesome v5 y v6
        patterns = [
            r'^(fas|far|fal|fad|fab|fa)\s+fa-[\w-]+',      # fas fa-user (v5)
            r'^fa-(solid|regular|light|duotone|brands)\s+fa-[\w-]+',  # fa-solid fa-user (v6)
            r'^fa-[\w-]+$',                                 # fa-user (formato simple)
        ]
        
        is_valid = any(re.match(pattern, icon) for pattern in patterns)
        
        if not is_valid:
            raise forms.ValidationError(
                "Formato de ícono inválido. Ejemplos válidos: "
                "'fas fa-user', 'fa-solid fa-person', 'fa-home'"
            )
        
        return icon