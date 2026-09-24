from django import forms
from django.forms import ModelForm
from applications.core.models import Cargo


class CargoForm(ModelForm):
    class Meta:
        model = Cargo
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese el nombre del cargo',
                    'maxlength': '100',
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 transition-colors',
                    'onkeyup': 'previewChanges()',
                    'onblur': 'validateField(this)',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'placeholder': 'Descripción del cargo (opcional)',
                    'rows': 3,
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 transition-colors resize-none',
                    'onkeyup': 'previewChanges()',
                    'onblur': 'validateField(this)',
                }
            ),
            'activo': forms.CheckboxInput(
                attrs={
                    'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600',
                    'onchange': 'previewChanges()',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar etiquetas con estilos consistentes
        self.fields['nombre'].label = 'Nombre del Cargo'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['activo'].label = 'Activo'
        
        # Configurar help_text para cada campo
        self.fields['nombre'].help_text = 'Ingrese el nombre del cargo (ej.: Médico, Enfermero, Administrador)'
        self.fields['descripcion'].help_text = 'Descripción opcional del rol que cumple este cargo'
        self.fields['activo'].help_text = 'Desmarque para desactivar este cargo'

    def clean_nombre(self):
        """Validar que el nombre del cargo no esté vacío y no contenga solo espacios."""
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip()
            if not nombre:
                raise forms.ValidationError('El nombre del cargo no puede estar vacío.')
            # Validar que no exista otro cargo activo con el mismo nombre (excluyendo el actual)
            if self.instance and self.instance.pk:
                if Cargo.objects.filter(nombre__iexact=nombre, activo=True).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un cargo activo con este nombre.')
            else:
                if Cargo.objects.filter(nombre__iexact=nombre, activo=True).exists():
                    raise forms.ValidationError('Ya existe un cargo activo con este nombre.')
        return nombre

    def clean(self):
        """Validación general del formulario."""
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        
        # Validar que se haya proporcionado al menos el nombre
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre del cargo es obligatorio.')
        
        return cleaned_data
