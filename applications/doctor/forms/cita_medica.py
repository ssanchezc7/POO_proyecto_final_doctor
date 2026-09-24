from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from datetime import date, datetime, time
from applications.doctor.models import CitaMedica
from applications.core.models import Doctor, Paciente
from applications.doctor.models import HorarioAtencion
from applications.doctor.utils.cita_medica import EstadoCitaChoices


class CustomDateInput(forms.DateInput):
    """Widget personalizado para asegurar que las fechas se carguen correctamente"""
    def __init__(self, attrs=None, format='%Y-%m-%d'):
        default_attrs = {
            'type': 'date',
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)
    
    def format_value(self, value):
        """Asegurar que el valor se formatee correctamente"""
        if value is None:
            return ''
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        return value


class CustomTimeInput(forms.TimeInput):
    """Widget personalizado para asegurar que las horas se carguen correctamente"""
    def __init__(self, attrs=None, format='%H:%M'):
        default_attrs = {
            'type': 'time',
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'readonly': True
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)
    
    def format_value(self, value):
        """Asegurar que el valor se formatee correctamente"""
        if value is None:
            return ''
        if isinstance(value, time):
            return value.strftime('%H:%M')
        return value


class CitaMedicaForm(ModelForm):
    class Meta:
        model = CitaMedica
        fields = [
            "paciente",
            "doctor", 
            "fecha",
            "hora_cita",
            "estado",
            "observaciones",
        ]
        widgets = {
            "paciente": forms.Select(attrs={
                "id": "id_paciente",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "doctor": forms.Select(attrs={
                "id": "id_doctor",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                "onchange": "cargarCalendario()"
            }),
            "fecha": CustomDateInput(attrs={
                "id": "id_fecha",
                "min": date.today().isoformat(),
            }),
            "hora_cita": CustomTimeInput(attrs={
                "id": "id_hora_cita",
            }),
            "estado": forms.Select(attrs={
                "id": "id_estado",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "observaciones": forms.Textarea(attrs={
                "placeholder": "Observaciones adicionales de la cita...",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none",
                "rows": 3,
            }),
        }
        labels = {
            "paciente": "Paciente",
            "doctor": "Doctor",
            "fecha": "Fecha",
            "hora_cita": "Hora de la Cita",
            "estado": "Estado",
            "observaciones": "Observaciones",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo doctores activos
        self.fields['doctor'].queryset = Doctor.objects.filter(activo=True).order_by('nombres', 'apellidos')
        
        # Filtrar solo pacientes activos
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).order_by('nombres', 'apellidos')
        
        # Configurar choices de estado
        self.fields['estado'].choices = EstadoCitaChoices.choices
        
        # Si es una actualización (tiene instancia), permitir fechas pasadas
        if self.instance and self.instance.pk:
            # Remover la restricción de fecha mínima para actualizaciones
            self.fields['fecha'].widget.attrs.pop('min', None)
            
            # Asegurar que los valores iniciales estén presentes
            if not self.initial.get('fecha') and self.instance.fecha:
                self.initial['fecha'] = self.instance.fecha
            if not self.initial.get('hora_cita') and self.instance.hora_cita:
                self.initial['hora_cita'] = self.instance.hora_cita

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        
        # Solo validar fechas futuras si es una nueva cita (no tiene instance o pk)
        if not (self.instance and self.instance.pk):
            if fecha and fecha < date.today():
                raise ValidationError("No se pueden agendar citas en fechas pasadas.")
        
        return fecha

    def clean_hora_cita(self):
        hora_cita = self.cleaned_data.get('hora_cita')
        fecha = self.cleaned_data.get('fecha')
        
        # Solo validar horas futuras si es una nueva cita (no tiene instance o pk)
        if not (self.instance and self.instance.pk):
            if fecha and hora_cita:
                # Si es hoy, verificar que la hora no sea en el pasado
                if fecha == date.today():
                    ahora = datetime.now().time()
                    if hora_cita <= ahora:
                        raise ValidationError("No se pueden agendar citas en horas pasadas.")
        
        return hora_cita

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        fecha = cleaned_data.get('fecha')
        hora_cita = cleaned_data.get('hora_cita')
        
        if doctor and fecha and hora_cita:
            # Verificar que el doctor tenga horario de atención ese día
            dias_semana_map = {
                'monday': 'lunes',
                'tuesday': 'martes', 
                'wednesday': 'miércoles',
                'thursday': 'jueves',
                'friday': 'viernes',
                'saturday': 'sábado',
                'sunday': 'domingo'
            }
            dia_semana_ingles = fecha.strftime('%A').lower()
            dia_semana = dias_semana_map.get(dia_semana_ingles, dia_semana_ingles)
            
            horarios = doctor.horarios_atencion.filter(
                dia_semana=dia_semana,
                activo=True
            )
            
            if not horarios.exists():
                raise ValidationError(f"El doctor no tiene horario de atención el día {fecha.strftime('%A')}.")
            
            # Verificar que la hora esté dentro del horario de atención
            hora_valida = False
            for horario in horarios:
                if horario.hora_inicio <= hora_cita <= horario.hora_fin:
                    # Verificar si está en el intervalo de descanso
                    if horario.intervalo_desde and horario.intervalo_hasta:
                        if horario.intervalo_desde <= hora_cita < horario.intervalo_hasta:
                            continue
                    hora_valida = True
                    break
            
            if not hora_valida:
                raise ValidationError("La hora seleccionada no está dentro del horario de atención del doctor.")
            
            # Verificar que no exista otra cita en el mismo horario
            cita_existente = CitaMedica.objects.filter(
                doctor=doctor,
                fecha=fecha,
                hora_cita=hora_cita
            )
            
            # Si estamos editando, excluir la cita actual
            if self.instance.pk:
                cita_existente = cita_existente.exclude(pk=self.instance.pk)
            
            if cita_existente.exists():
                raise ValidationError("Ya existe una cita agendada para este doctor en esta fecha y hora.")

        return cleaned_data


class CitaMedicaCalendarioForm(forms.Form):
    """Formulario para seleccionar doctor y navegar por el calendario"""
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(activo=True).order_by('nombres', 'apellidos'),
        widget=forms.Select(attrs={
            "id": "calendario_doctor",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            "onchange": "cambiarDoctor(this.value)"
        }),
        empty_label="Seleccione un doctor"
    )
    
    anio = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            "id": "calendario_anio",
            "class": "block w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            "min": date.today().year,
            "max": date.today().year + 2,
            "onchange": "cambiarPeriodo()"
        }),
        initial=date.today().year
    )
    
    mes = forms.ChoiceField(
        choices=[
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
            (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
            (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ],
        widget=forms.Select(attrs={
            "id": "calendario_mes",
            "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            "onchange": "cambiarPeriodo()"
        }),
        initial=date.today().month
    )
