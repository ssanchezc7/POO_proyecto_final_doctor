from django import forms
from django.contrib.auth.models import Group


class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
                })
            elif isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                    'placeholder': f'Ingrese {field.label.lower()}'
                })

    class Meta:
        model = Group
        fields = [
            'name',
        ]
        
        labels = {
            'name': 'Nombre del Grupo',
        }
        
        help_texts = {
            'name': 'Nombre único para identificar el grupo de usuarios',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            # Verificar que no exista otro grupo con el mismo nombre (excluyendo el actual en edición)
            existing_group = Group.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing_group = existing_group.exclude(pk=self.instance.pk)
            
            if existing_group.exists():
                raise forms.ValidationError('Ya existe un grupo con este nombre.')
        
        return name

    def save(self, commit=True):
        group = super().save(commit=False)
        
        if commit:
            group.save()
            
        return group
