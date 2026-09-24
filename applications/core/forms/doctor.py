from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from applications.core.models import Doctor, Especialidad
from applications.doctor.models import HorarioAtencion
from applications.doctor.utils.doctor import DiaSemanaChoices

User = get_user_model()

class DateInputWidget(forms.DateInput):
    """Widget personalizado para campos de fecha que asegura el formato correcto"""
    
    def __init__(self, attrs=None, format=None):
        default_attrs = {'type': 'date'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y-%m-%d')
    
    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        # Asegurar que el valor se formatee correctamente para input type="date"
        return value.strftime('%Y-%m-%d') if value else ''


class DoctorForm(ModelForm):
    
    class Meta:
        model = Doctor
        fields = [
            "nombres",
            "apellidos", 
            "ruc",
            "fecha_nacimiento",
            "direccion",
            "latitud",
            "longitud",
            "codigo_unico_doctor",
            "especialidad",
            "horarios_atencion",
            "telefonos",
            "email",
            "duracion_atencion",
            "curriculum",
            "firma_digital",
            "foto",
            "imagen_receta",
            "activo",
        ]
        error_messages = {
            "ruc": {
                "unique": "Ya existe un doctor con este RUC.",
            },
            "codigo_unico_doctor": {
                "unique": "Ya existe un doctor con este código único.",
            },
            "direccion": {
                "unique": "Ya existe un doctor registrado en esta dirección.",
            },
        }
        widgets = {
            "nombres": forms.TextInput(attrs={
            "placeholder": "Nombres del doctor",
            "id": "id_nombres",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "apellidos": forms.TextInput(attrs={
            "placeholder": "Apellidos del doctor",
            "id": "id_apellidos",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "ruc": forms.TextInput(attrs={
            "placeholder": "1234567890001",
            "id": "id_ruc",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            "maxlength": "13",
            }),
            "fecha_nacimiento": DateInputWidget(attrs={
            "id": "id_fecha_nacimiento",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "direccion": forms.Textarea(attrs={
            "placeholder": "Dirección completa del consultorio o lugar de trabajo",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
            "rows": 2,
            }),
            "latitud": forms.NumberInput(attrs={
            "placeholder": "-0.123456",
            "id": "id_latitud",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            "step": "any",
            }),
            "longitud": forms.NumberInput(attrs={
            "placeholder": "-78.123456",
            "id": "id_longitud",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            "step": "any",
            }),
            "codigo_unico_doctor": forms.TextInput(attrs={
            "placeholder": "DOC-001",
            "id": "id_codigo_unico_doctor",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "especialidad": forms.SelectMultiple(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'size': '8',
                'multiple': True,
                'style': 'min-height: 150px;',
            }),
            "telefonos": forms.TextInput(attrs={
            "placeholder": "0987654321",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "doctor@ejemplo.com",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "horarios_atencion": forms.SelectMultiple(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'size': '8',
                'multiple': True,
                'style': 'min-height: 150px;',
            }),
            "duracion_atencion": forms.NumberInput(attrs={
            "placeholder": "30",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            "min": "1",
            "max": "180",
            }),
            "curriculum": forms.FileInput(attrs={
            "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
            "accept": ".pdf,.doc,.docx",
            }),
            "firma_digital": forms.FileInput(attrs={
            "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
            "accept": "image/*",
            }),
            "foto": forms.FileInput(attrs={
            "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
            "accept": "image/*",
            }),
            "imagen_receta": forms.FileInput(attrs={
            "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
            "accept": "image/*",
            }),
            "activo": forms.CheckboxInput(attrs={
            "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
        }

    def __init__(self, *args, **kwargs):
        """Inicializar el formulario con configuraciones adicionales"""
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para especialidades activas
        especialidades = Especialidad.objects.filter(activo=True).order_by('nombre')
        self.fields['especialidad'].queryset = especialidades
        self.fields['especialidad'].empty_label = None
        
        # Configurar queryset para horarios de atención con mejor organización
        horarios_queryset = HorarioAtencion.objects.filter(activo=True).order_by('dia_semana', 'hora_inicio')
        self.fields['horarios_atencion'].queryset = horarios_queryset
        
        # Mejorar la presentación de los horarios
        if horarios_queryset.exists():
            # Crear opciones organizadas por día
            self.fields['horarios_atencion'].widget.attrs.update({
                'data-toggle': 'horarios-selection',
                'data-description': f'Disponibles: {horarios_queryset.count()} horarios'
            })
        
        # Configurar fecha límite para fecha de nacimiento (mayor de 18 años)
        fecha_maxima = date.today() - timedelta(days=18*365)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = fecha_maxima.strftime('%Y-%m-%d')
        
        # Configurar campos requeridos
        self.fields['email'].required = True
        self.fields['horarios_atencion'].required = True
        self.fields['especialidad'].required = True
        
        # Configurar ayuda para especialidades
        if especialidades.exists():
            self.fields['especialidad'].help_text = f"Disponibles: {especialidades.count()} especialidades. Selecciona al menos una."
        else:
            self.fields['especialidad'].help_text = "⚠️ No hay especialidades disponibles. Contacte al administrador."
            self.fields['especialidad'].widget.attrs['disabled'] = True
            
        # Configurar ayuda dinámica para horarios
        if horarios_queryset.exists():
            dias_disponibles = set()
            for horario in horarios_queryset:
                dias_disponibles.add(horario.get_dia_semana_display())
            self.fields['horarios_atencion'].help_text = f"Selecciona uno o más horarios de atención. Días disponibles: {', '.join(sorted(dias_disponibles))}"
        else:
            self.fields['horarios_atencion'].help_text = "⚠️ No hay horarios disponibles. Contacte al administrador para crear horarios."
        
        # Si estamos editando, mantener los valores existentes
        if self.instance.pk:
            # Precargar especialidades seleccionadas
            if hasattr(self.instance, 'especialidad'):
                self.initial['especialidad'] = self.instance.especialidad.all()
            
            # Precargar horarios seleccionados
            if hasattr(self.instance, 'horarios_atencion'):
                self.initial['horarios_atencion'] = self.instance.horarios_atencion.all()

    def clean(self):
        """Validaciones generales del formulario"""
        cleaned_data = super().clean()
        
        # Verificar que haya especialidades disponibles
        especialidades = cleaned_data.get('especialidad')
        if not especialidades or not especialidades.exists():
            raise forms.ValidationError("Debe seleccionar al menos una especialidad médica.")
        
        # Verificar que haya horarios seleccionados
        horarios_atencion = cleaned_data.get('horarios_atencion')
        if not horarios_atencion or not horarios_atencion.exists():
            raise forms.ValidationError("Debe seleccionar al menos un horario de atención.")
        
        return cleaned_data

    def clean_fecha_nacimiento(self):
        """Validar que el doctor sea mayor de edad"""
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18:
                raise forms.ValidationError("El doctor debe ser mayor de 18 años.")
        return fecha_nacimiento

    def clean_email(self):
        """Validar que el email no esté en uso por otro doctor"""
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si ya existe otro doctor con este email
            existing_doctor = Doctor.objects.filter(email=email)
            if self.instance.pk:
                existing_doctor = existing_doctor.exclude(pk=self.instance.pk)
            
            if existing_doctor.exists():
                raise forms.ValidationError("Ya existe un doctor registrado con este correo electrónico.")
                
            # Verificar si ya existe un usuario con este email
            if User.objects.filter(email=email).exists():
                # Si estamos editando y el usuario ya tiene este email, permitirlo
                if not (self.instance.pk and User.objects.filter(email=email, username=email).exists()):
                    raise forms.ValidationError("Ya existe un usuario registrado con este correo electrónico.")
        
        return email

    def clean_duracion_atencion(self):
        """Validar duración de atención"""
        duracion = self.cleaned_data.get('duracion_atencion')
        if duracion and (duracion < 15 or duracion > 180):
            raise forms.ValidationError("La duración de atención debe estar entre 15 y 180 minutos.")
        return duracion

    def generate_password(self):
        """Generar contraseña aleatoria"""
        length = 12
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for i in range(length))
        return password

    def create_user_account(self, doctor):
        """Crear cuenta de usuario para el doctor"""
        if not doctor.email:
            return None, None
            
        try:
            # Generar contraseña
            password = self.generate_password()
            
            # Crear usuario
            user = User.objects.create_user(
                username=doctor.email,
                email=doctor.email,
                first_name=doctor.nombres,
                last_name=doctor.apellidos,
                password=password
            )
            
            # Asignar al grupo de doctores
            doctors_group, created = Group.objects.get_or_create(name='Doctores')
            user.groups.add(doctors_group)
            
            return user, password
            
        except Exception as e:
            print(f"Error creating user account: {e}")
            return None, None

    def send_credentials_email(self, doctor, password):
        """Enviar credenciales por correo"""
        try:
            subject = 'Bienvenido al Sistema Médico - Credenciales de Acceso'
            message = f"""
Estimado Dr. {doctor.nombre_completo},

Le damos la bienvenida al Sistema Médico. Sus credenciales de acceso son:

Usuario: {doctor.email}
Contraseña: {password}

Por favor, cambie su contraseña en el primer acceso por seguridad.

URL del sistema: {settings.LOGIN_URL}

Saludos cordiales,
Equipo de Sistemas
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [doctor.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def save(self, commit=True):
        """Guardar doctor y crear cuenta de usuario si es necesario"""
        doctor = super().save(commit=commit)
        
        if commit and doctor.email:
            # Verificar si ya tiene cuenta de usuario
            existing_user = User.objects.filter(email=doctor.email).first()
            
            if not existing_user:
                # Crear nueva cuenta
                user, password = self.create_user_account(doctor)
                if user and password:
                    # Enviar credenciales por correo
                    self.send_credentials_email(doctor, password)
        
        return doctor
