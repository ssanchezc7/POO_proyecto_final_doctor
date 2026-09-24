from django import forms
from django.contrib.auth.models import Group, Permission
from applications.security.models import Module, GroupModulePermission


class GroupModulePermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el campo de grupo
        self.fields['group'].widget.attrs.update({
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'id': 'id_group'
        })
        
        # Configurar el campo de módulo
        self.fields['module'].widget.attrs.update({
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'id': 'id_module'
        })
        
        # Configurar el campo de permisos como checkboxes
        self.fields['permissions'].widget = forms.CheckboxSelectMultiple(attrs={
            'class': 'permission-checkbox'
        })
        
        # Configurar el queryset de permisos de forma segura
        self._setup_permissions_queryset()

    def _setup_permissions_queryset(self):
        """Configura el queryset de permisos de forma segura"""
        # IMPORTANTE: Siempre incluir todos los permisos en el queryset para evitar 
        # errores de validación de Django cuando se seleccionan permisos dinámicamente
        # La validación real se hace en clean_permissions()
        self.fields['permissions'].queryset = Permission.objects.all().order_by('content_type__model', 'name')
    
    def clean_permissions(self):
        """Validación personalizada para permisos"""
        permissions = self.cleaned_data.get('permissions')
        module = self.cleaned_data.get('module')
        
        # Si no hay permisos seleccionados, está bien (puede ser intencional)
        if not permissions:
            return permissions
            
        # Si no hay módulo, no podemos validar
        if not module:
            return permissions
        
        # Obtener los permisos válidos para este módulo
        valid_permissions = module.permissions.all()
        
        # Si el módulo no tiene permisos específicos, no permitir ninguno
        if not valid_permissions.exists():
            raise forms.ValidationError(
                f'El módulo "{module.name}" no tiene permisos específicos asignados. '
                f'Configura primero los permisos en la gestión de módulos antes de poder asignarlos a grupos.'
            )
        
        # Validar que todos los permisos seleccionados sean válidos para este módulo
        invalid_permissions = []
        valid_permission_ids = set(valid_permissions.values_list('id', flat=True))
        
        for permission in permissions:
            if permission.id not in valid_permission_ids:
                invalid_permissions.append(permission.name)
        
        if invalid_permissions:
            raise forms.ValidationError(
                f'Los siguientes permisos no están permitidos para el módulo "{module.name}": '
                f'{", ".join(invalid_permissions)}. '
                f'Solo puedes seleccionar permisos que estén asociados al módulo seleccionado.'
            )
        
        return permissions

    class Meta:
        model = GroupModulePermission
        fields = ['group', 'module', 'permissions']
        labels = {
            'group': 'Grupo',
            'module': 'Módulo',
            'permissions': 'Permisos',
        }
        help_texts = {
            'group': 'Selecciona el grupo al que asignar permisos',
            'module': 'Selecciona el módulo sobre el cual otorgar permisos',
            'permissions': 'Marca los permisos que tendrá este grupo sobre el módulo seleccionado',
        }

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        module = cleaned_data.get('module')
        
        if group and module:
            # Verificar si ya existe esta combinación (excluyendo la instancia actual)
            existing = GroupModulePermission.objects.filter(group=group, module=module)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Ya existe una asignación de permisos para el grupo "{group.name}" y el módulo "{module.name}". '
                    f'Puedes editarla en lugar de crear una nueva.'
                )
        
        return cleaned_data
