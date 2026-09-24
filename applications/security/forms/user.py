import re
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import Group
from applications.security.models import User

class UserForm(ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Ingrese contraseña",
            "id": "id_password",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }),
        required=False,
        help_text="Dejar en blanco para mantener la contraseña actual"
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirme contraseña",
            "id": "id_confirm_password",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }),
        required=False,
        help_text="Confirme la contraseña"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "dni",
            "direction",
            "phone",
            "groups",
            "is_active",
            "is_staff",
            "image",
        ]
        error_messages = {
            "username": {
                "unique": "Ya existe un usuario con este nombre de usuario.",
            },
            "email": {
                "unique": "Ya existe un usuario con este email.",
            },
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Ingrese nombre de usuario",
                "id": "id_username",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Ingrese email del usuario",
                "id": "id_email",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "first_name": forms.TextInput(attrs={
                "placeholder": "Ingrese nombres",
                "id": "id_first_name",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Ingrese apellidos",
                "id": "id_last_name",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "dni": forms.TextInput(attrs={
                "placeholder": "Ingrese cédula o RUC",
                "id": "id_dni",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "direction": forms.TextInput(attrs={
                "placeholder": "Ingrese dirección",
                "id": "id_direction",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Ingrese teléfono",
                "id": "id_phone",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "groups": forms.CheckboxSelectMultiple(attrs={
                "class": "form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out",
            }),
            "is_staff": forms.CheckboxInput(attrs={
                "class": "form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("El email es obligatorio.")
        
        # Validar formato de email con regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError("El formato del email no es válido.")
        
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            # Validar que solo contenga números
            if not dni.isdigit():
                raise forms.ValidationError("La cédula debe contener solo números.")
            
            # Validar longitud
            if len(dni) not in [10, 13]:
                raise forms.ValidationError("La cédula debe tener 10 dígitos (cédula) o 13 dígitos (RUC).")
        
        return dni

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remover espacios y guiones
            phone = re.sub(r'[\s-]', '', phone)
            
            # Validar que contenga solo números y/o el signo +
            if not re.match(r'^\+?[0-9]+$', phone):
                raise forms.ValidationError("El teléfono debe contener solo números.")
        
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Solo validar passwords si se está creando un nuevo usuario o si se proporcionó una nueva contraseña
        if self.instance.pk is None or password:  # Nuevo usuario o cambio de contraseña
            if not password:
                raise forms.ValidationError("La contraseña es obligatoria para nuevos usuarios.")
            
            if password != confirm_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            
            if len(password) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        # Solo cambiar la contraseña si se proporcionó una nueva
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            self.save_m2m()  # Para guardar las relaciones many-to-many (groups)
        
        return user
