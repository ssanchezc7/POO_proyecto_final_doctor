from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date, timedelta
from applications.core.models import Paciente, TipoSangre


class PacienteForm(ModelForm):
    class Meta:
        model = Paciente
        fields = [
            "nombres",
            "apellidos", 
            "cedula_ecuatoriana",
            "dni",
            "fecha_nacimiento",
            "telefono",
            "email",
            "sexo",
            "estado_civil",
            "direccion",
            "latitud",
            "longitud",
            "tipo_sangre",
            "foto",
            "antecedentes_personales",
            "antecedentes_quirurgicos",
            "antecedentes_familiares",
            "alergias",
            "medicamentos_actuales",
            "habitos_toxicos",
            "vacunas",
            "antecedentes_gineco_obstetricos",
            "activo",
        ]
        error_messages = {
            "cedula_ecuatoriana": {
                "unique": "Ya existe un paciente con esta cédula.",
            },
            "email": {
                "unique": "Ya existe un paciente con este correo electrónico.",
            },
        }
        widgets = {
            "nombres": forms.TextInput(attrs={
                "placeholder": "Nombres del paciente",
                "id": "id_nombres",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "apellidos": forms.TextInput(attrs={
                "placeholder": "Apellidos del paciente",
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
            "fecha_nacimiento": forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    "type": "date",
                    "id": "id_fecha_nacimiento",
                    "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                }
            ),
            "telefono": forms.TextInput(attrs={
                "placeholder": "Número(s) de teléfono",
                "id": "id_telefono",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "correo@ejemplo.com",
                "id": "id_email",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "sexo": forms.Select(attrs={
                "id": "id_sexo",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "estado_civil": forms.Select(attrs={
                "id": "id_estado_civil",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "direccion": forms.Textarea(attrs={
                "placeholder": "Dirección completa del paciente",
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
            "tipo_sangre": forms.Select(attrs={
                "id": "id_tipo_sangre",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "foto": forms.ClearableFileInput(attrs={
                "id": "id_foto",
                "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                "accept": "image/*",
            }),
            "antecedentes_personales": forms.Textarea(attrs={
                "placeholder": "Diabetes tipo 2, hipertensión, asma, etc.",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "antecedentes_quirurgicos": forms.Textarea(attrs={
                "placeholder": "Apendicectomía, cesárea, etc.",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "antecedentes_familiares": forms.Textarea(attrs={
                "placeholder": "Enfermedades hereditarias en la familia",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "alergias": forms.Textarea(attrs={
                "placeholder": "Penicilina, mariscos, polvo, etc.",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "medicamentos_actuales": forms.Textarea(attrs={
                "placeholder": "Losartán 50mg diario, Metformina 850mg cada 12 horas",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "habitos_toxicos": forms.TextInput(attrs={
                "placeholder": "Tabaco, alcohol, drogas, sedentarismo, etc.",
                "id": "id_habitos_toxicos",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "vacunas": forms.Textarea(attrs={
                "placeholder": "COVID-19, influenza, etc.",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
            "antecedentes_gineco_obstetricos": forms.Textarea(attrs={
                "placeholder": "Solo en mujeres: menarquia, embarazos, anticonceptivos",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
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
            "telefono": "Teléfono(s)",
            "email": "Correo Electrónico",
            "sexo": "Sexo",
            "estado_civil": "Estado Civil",
            "direccion": "Dirección",
            "latitud": "Latitud",
            "longitud": "Longitud",
            "tipo_sangre": "Tipo de Sangre",
            "foto": "Foto del Paciente",
            "antecedentes_personales": "Antecedentes Personales",
            "antecedentes_quirurgicos": "Antecedentes Quirúrgicos",
            "antecedentes_familiares": "Antecedentes Familiares",
            "alergias": "Alergias",
            "medicamentos_actuales": "Medicamentos Actuales",
            "habitos_toxicos": "Hábitos Tóxicos",
            "vacunas": "Vacunas",
            "antecedentes_gineco_obstetricos": "Antecedentes Gineco-Obstétricos",
            "activo": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar tipos de sangre por tipo
        self.fields['tipo_sangre'].queryset = TipoSangre.objects.all().order_by('tipo')
        
        # Configurar el formato de fecha para el widget
        self.fields['fecha_nacimiento'].input_formats = ['%Y-%m-%d']
        
        # Establecer fechas límite
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Fecha de nacimiento: máximo ayer (no pueden nacer hoy o en el futuro)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = yesterday.strftime('%Y-%m-%d')

    def clean_nombres(self):
        nombres = self.cleaned_data.get("nombres")
        if nombres:
            nombres = nombres.strip().title()
            
            if not nombres:
                raise forms.ValidationError("Los nombres del paciente no pueden estar vacíos.")
            
            if len(nombres) < 2:
                raise forms.ValidationError("Los nombres deben tener al menos 2 caracteres.")
                
            return nombres
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get("apellidos")
        if apellidos:
            apellidos = apellidos.strip().title()
            
            if not apellidos:
                raise forms.ValidationError("Los apellidos del paciente no pueden estar vacíos.")
            
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

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if telefono:
            telefono = telefono.strip()
            
            if not telefono:
                raise forms.ValidationError("El teléfono no puede estar vacío.")
            
            if len(telefono) < 7:
                raise forms.ValidationError("El teléfono debe tener al menos 7 dígitos.")
                
            return telefono
        return telefono

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
            
            # Validar edad máxima (por ejemplo, 150 años)
            edad_maxima = today.replace(year=today.year - 150)
            if fecha_nacimiento < edad_maxima:
                raise forms.ValidationError("La fecha de nacimiento no puede ser anterior a 150 años.")
                
            return fecha_nacimiento
        return fecha_nacimiento

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip().lower()
            
            # Verificar formato básico
            if "@" not in email or "." not in email:
                raise forms.ValidationError("Ingrese un correo electrónico válido.")
                
            return email
        return email

    def clean_habitos_toxicos(self):
        habitos_toxicos = self.cleaned_data.get("habitos_toxicos")
        if habitos_toxicos:
            habitos_toxicos = habitos_toxicos.strip().lower()
            
            if not habitos_toxicos:
                return "ninguno"
                
            return habitos_toxicos
        return "ninguno"
