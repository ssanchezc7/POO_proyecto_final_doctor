from django import forms
from django.forms import ModelForm
from applications.doctor.models import HorarioAtencion
from applications.doctor.utils.doctor import DiaSemanaChoices


class HorarioAtencionForm(ModelForm):
    class Meta:
        model = HorarioAtencion
        fields = [
            "dia_semana",
            "hora_inicio",
            "hora_fin",
            "intervalo_desde",
            "intervalo_hasta",
            "activo",
        ]
        error_messages = {
            "dia_semana": {
                "required": "Debe seleccionar un día de la semana.",
            },
            "hora_inicio": {
                "required": "Debe especificar la hora de inicio.",
            },
            "hora_fin": {
                "required": "Debe especificar la hora de fin.",
            },
        }
        widgets = {
            "dia_semana": forms.Select(attrs={
                "id": "id_dia_semana",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "hora_inicio": forms.TimeInput(attrs={
                "type": "time",
                "id": "id_hora_inicio",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "hora_fin": forms.TimeInput(attrs={
                "type": "time",
                "id": "id_hora_fin",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "intervalo_desde": forms.TimeInput(attrs={
                "type": "time",
                "id": "id_intervalo_desde",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "intervalo_hasta": forms.TimeInput(attrs={
                "type": "time",
                "id": "id_intervalo_hasta",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
            }),
        }
        labels = {
            "dia_semana": "Día de la Semana",
            "hora_inicio": "Hora de Inicio",
            "hora_fin": "Hora de Fin",
            "intervalo_desde": "Intervalo desde",
            "intervalo_hasta": "Intervalo hasta",
            "activo": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar opciones de días comunes
        self.fields['dia_semana'].empty_label = "Seleccione un día"
        
        # Configurar valores por defecto para campos de tiempo
        if not self.instance.pk:  # Solo para nuevos horarios
            self.fields['hora_inicio'].widget.attrs['value'] = '08:00'
            self.fields['hora_fin'].widget.attrs['value'] = '17:00'
            self.fields['intervalo_desde'].widget.attrs['value'] = '12:00'
            self.fields['intervalo_hasta'].widget.attrs['value'] = '13:00'

    def clean(self):
        cleaned_data = super().clean()
        dia_semana = cleaned_data.get("dia_semana")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")
        intervalo_desde = cleaned_data.get("intervalo_desde")
        intervalo_hasta = cleaned_data.get("intervalo_hasta")

        # Validar que la hora de fin sea posterior a la hora de inicio
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

        # Validar intervalo de descanso
        if intervalo_desde and intervalo_hasta:
            if intervalo_hasta <= intervalo_desde:
                raise forms.ValidationError("La hora de fin del intervalo debe ser posterior a la hora de inicio del intervalo.")
            
            # Validar que el intervalo esté dentro del horario laboral
            if hora_inicio and hora_fin:
                if intervalo_desde < hora_inicio or intervalo_hasta > hora_fin:
                    raise forms.ValidationError("El intervalo de descanso debe estar dentro del horario de trabajo.")
        
        # Validar que si se especifica un campo de intervalo, se especifique el otro
        if (intervalo_desde and not intervalo_hasta) or (intervalo_hasta and not intervalo_desde):
            raise forms.ValidationError("Si especifica un intervalo de descanso, debe completar tanto la hora de inicio como la hora de fin del intervalo.")

        # Verificar unicidad de horario (excepto para el objeto actual en edición)
        if dia_semana and hora_inicio and hora_fin:
            existing_horarios = HorarioAtencion.objects.filter(
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
            
            # Excluir el objeto actual si estamos editando
            if self.instance.pk:
                existing_horarios = existing_horarios.exclude(pk=self.instance.pk)
            
            if existing_horarios.exists():
                raise forms.ValidationError(f"Ya existe un horario para {dia_semana} de {hora_inicio} a {hora_fin}.")

        return cleaned_data

    def clean_dia_semana(self):
        dia_semana = self.cleaned_data.get("dia_semana")
        if dia_semana:
            return dia_semana.lower()
        return dia_semana
