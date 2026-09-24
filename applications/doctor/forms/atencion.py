
from django import forms
from django.forms import ModelForm
from applications.doctor.models import Atencion


class AtencionForm(ModelForm):
    class Meta:
        model = Atencion
        fields = '__all__'

        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-select w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'presion_arterial': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'placeholder': 'Ej: 120/80 mmHg'
            }),
            'pulso': forms.NumberInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'temperatura': forms.NumberInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'frecuencia_respiratoria': forms.NumberInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'saturacion_oxigeno': forms.NumberInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'motivo_consulta': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'rows': 3
            }),
            'sintomas': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'rows': 3
            }),
            'tratamiento': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'rows': 3
            }),
            'diagnostico': forms.SelectMultiple(attrs={
                'class': 'form-multiselect w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'examen_fisico': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'rows': 2
            }),
            'examenes_enviados': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'rows': 2
            }),
            'comentario_adicional': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'rows': 2
            }),
            'es_control': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }
