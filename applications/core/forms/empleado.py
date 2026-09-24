from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date, timedelta
from applications.core.models import Empleado, Cargo


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


class EmpleadoForm(ModelForm):
    class Meta:
        model = Empleado
        fields = [
            "nombres",
            "apellidos", 
            "cedula_ecuatoriana",
            "dni",
            "fecha_nacimiento",
            "cargo",
            "sueldo",
            "fecha_ingreso",
            "direccion",
            "latitud",
            "longitud",
            "foto",
            "activo",
        ]
        error_messages = {
            "cedula_ecuatoriana": {
                "unique": "Ya existe un empleado con esta cédula.",
            },
            "sueldo": {
                "invalid": "Ingrese un valor numérico válido para el sueldo.",
            },
        }
        widgets = {
            "nombres": forms.TextInput(attrs={
                "placeholder": "Nombres del empleado",
                "id": "id_nombres",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "apellidos": forms.TextInput(attrs={
                "placeholder": "Apellidos del empleado",
                "id": "id_apellidos",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "cedula_ecuatoriana": forms.TextInput(attrs={
                "placeholder": "1234567890",
                "id": "id_cedula_ecuatoriana",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                "maxlength": "10",
            }),
            "dni": forms.TextInput(attrs={
                "placeholder": "Documento internacional (opcional)",
                "id": "id_dni",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "fecha_nacimiento": DateInputWidget(attrs={
                "id": "id_fecha_nacimiento",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "cargo": forms.Select(attrs={
                "id": "id_cargo",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "sueldo": forms.NumberInput(attrs={
                "placeholder": "0.00",
                "id": "id_sueldo",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                "step": "0.01",
                "min": "0",
            }),
            "fecha_ingreso": DateInputWidget(attrs={
                "id": "id_fecha_ingreso",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "direccion": forms.Textarea(attrs={
                "placeholder": "Dirección completa del empleado",
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
            "foto": forms.ClearableFileInput(attrs={
                "id": "id_foto",
                "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                "accept": "image/*",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
        }
        labels = {
            "nombres": "Nombres",
            "apellidos": "Apellidos",
            "cedula_ecuatoriana": "Cédula Ecuatoriana", 
            "dni": "DNI Internacional",
            "fecha_nacimiento": "Fecha de Nacimiento",
            "cargo": "Cargo",
            "sueldo": "Sueldo",
            "fecha_ingreso": "Fecha de Ingreso",
            "direccion": "Dirección",
            "latitud": "Latitud",
            "longitud": "Longitud", 
            "foto": "Foto del Empleado",
            "activo": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo cargos activos
        self.fields['cargo'].queryset = Cargo.objects.filter(activo=True).order_by('nombre')
        
        # Establecer fechas límite
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Si estamos editando un empleado existente (instance existe)
        if self.instance and self.instance.pk:
            # Para edición: permitir la fecha existente pero limitar hacia el futuro
            # Fecha de nacimiento: máximo ayer
            self.fields['fecha_nacimiento'].widget.attrs['max'] = yesterday.strftime('%Y-%m-%d')
            
            # Fecha de ingreso: si la fecha actual es anterior a hoy, permitirla
            # pero no permitir fechas futuras más allá de 1 año
            max_future_date = today + timedelta(days=365)
            self.fields['fecha_ingreso'].widget.attrs['max'] = max_future_date.strftime('%Y-%m-%d')
            
            # No establecer min para fecha_ingreso en modo edición para permitir fechas pasadas existentes
        else:
            # Para creación: aplicar restricciones normales
            # Fecha de nacimiento: máximo ayer (no pueden nacer hoy o en el futuro)
            self.fields['fecha_nacimiento'].widget.attrs['max'] = yesterday.strftime('%Y-%m-%d')
            
            # Fecha de ingreso: mínimo hoy (no pueden ingresar en el pasado)
            self.fields['fecha_ingreso'].widget.attrs['min'] = today.strftime('%Y-%m-%d')

    def clean_nombres(self):
        nombres = self.cleaned_data.get("nombres")
        if nombres:
            nombres = nombres.strip().title()
            
            if not nombres:
                raise forms.ValidationError("Los nombres del empleado no pueden estar vacíos.")
            
            if len(nombres) < 2:
                raise forms.ValidationError("Los nombres deben tener al menos 2 caracteres.")
                
            return nombres
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get("apellidos")
        if apellidos:
            apellidos = apellidos.strip().title()
            
            if not apellidos:
                raise forms.ValidationError("Los apellidos del empleado no pueden estar vacíos.")
            
            if len(apellidos) < 2:
                raise forms.ValidationError("Los apellidos deben tener al menos 2 caracteres.")
                
            return apellidos
        return apellidos

    def clean_cedula_ecuatoriana(self):
        cedula = self.cleaned_data.get("cedula_ecuatoriana")
        if cedula:
            cedula = cedula.strip()
            
            if len(cedula) != 10:
                raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
            
            if not cedula.isdigit():
                raise forms.ValidationError("La cédula debe contener solo números.")
                
            return cedula
        return cedula

    def clean_sueldo(self):
        sueldo = self.cleaned_data.get("sueldo")
        if sueldo is not None:
            if sueldo < 0:
                raise forms.ValidationError("El sueldo no puede ser negativo.")
            
            if sueldo > 999999.99:
                raise forms.ValidationError("El sueldo no puede exceder $999,999.99.")
                
            return sueldo
        return sueldo

    def clean_direccion(self):
        direccion = self.cleaned_data.get("direccion")
        if direccion:
            direccion = direccion.strip()
            
            if not direccion:
                raise forms.ValidationError("La dirección no puede estar vacía.")
            
            if len(direccion) < 10:
                raise forms.ValidationError("La dirección debe tener al menos 10 caracteres.")
                
            return direccion
        return direccion

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get("fecha_nacimiento")
        if fecha_nacimiento:
            today = timezone.now().date()
            
            # No puede nacer hoy o en el futuro
            if fecha_nacimiento >= today:
                raise forms.ValidationError("La fecha de nacimiento no puede ser hoy o una fecha futura.")
            # Validar edad mínima (por ejemplo, 18 años)
            edad_minima = today.replace(year=today.year - 18)
            if fecha_nacimiento > edad_minima:
                raise forms.ValidationError("El empleado debe tener al menos 18 años de edad.")

            # Validar edad máxima (por ejemplo, 80 años)
            edad_maxima = today.replace(year=today.year - 80)
            if fecha_nacimiento < edad_maxima:
                raise forms.ValidationError("La fecha de nacimiento no puede ser anterior a 80 años.")
                
            return fecha_nacimiento
        return fecha_nacimiento

    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get("fecha_ingreso")
        if fecha_ingreso:
            today = timezone.now().date()
            
            # Si estamos editando un empleado existente, permitir fechas pasadas
            if not (self.instance and self.instance.pk):
                # Solo aplicar la restricción de fecha pasada para empleados nuevos
                if fecha_ingreso < today:
                    raise forms.ValidationError("La fecha de ingreso no puede ser anterior a hoy.")
            
            # Validar que no sea muy lejana en el futuro (por ejemplo, máximo 1 año)
            fecha_maxima = today.replace(year=today.year + 1)
            if fecha_ingreso > fecha_maxima:
                raise forms.ValidationError("La fecha de ingreso no puede ser superior a un año en el futuro.")
                
            return fecha_ingreso
        return fecha_ingreso
