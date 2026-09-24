import re
from django import forms
from django.forms import ModelForm

from applications.security.models import Menu, Module

class MenuForm(ModelForm):
    class Meta:
        model = Menu
        fields = [
            "name",
            "icon",
            "order",
           
        ]
        error_messages = {
          
            "name": {
                "unique": "Ya existe un menu con este nombre.",
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ingrese nombre del menu",
                "id": "id_name",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
          
            "icon": forms.TextInput(attrs={
                "placeholder": "Ingrese clase del ícono (ej. bi bi-house)",
                "id": "id_icon",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "order": forms.NumberInput(attrs={
                "placeholder": "Ingrese el orden",
                "id": "id_order",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
         
        }
        labels = {
            "name": "Nombre Menu",
            "icon": "Ícono",
            "order": "Orden",
            
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        return name.upper()
    
    def clean_icon(self):
        icon = self.cleaned_data['icon']
        if not icon:
            raise forms.ValidationError("El campo ícono es requerido.")
        
        # Patrones para FontAwesome v5 y v6
        patterns = [
            r'^(fas|far|fal|fad|fab|fa)\s+fa-\w+',      # fas fa-user (v5)
            r'^fa-(solid|regular|light|duotone|brands)\s+fa-\w+',  # fa-solid fa-user (v6)
            r'^fa-\w+$',                                 # fa-user (formato simple)
        ]
        
        is_valid = any(re.match(pattern, icon) for pattern in patterns)
        
        if not is_valid:
            raise forms.ValidationError(
                "Formato de ícono inválido. Ejemplos válidos: "
                "'fas fa-user', 'fa-solid fa-person', 'fa-home'"
            )
        
        return icon