from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from applications.core.models import (
    TipoSangre, Paciente, Especialidad, Doctor, Cargo, Empleado,
    TipoMedicamento, MarcaMedicamento, Medicamento,
    Diagnostico, TipoGasto, GastoMensual, FotoPaciente
)

@admin.register(TipoSangre)
class TipoSangreAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion')
    search_fields = ('tipo',)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cedula_ecuatoriana', 'email', 'sexo', 'estado_civil', 'tipo_sangre', 'activo')
    list_filter = ('sexo', 'estado_civil', 'activo', 'tipo_sangre')
    search_fields = ('nombres', 'apellidos', 'cedula_ecuatoriana', 'email')
    readonly_fields = ('edad', 'get_image')

    def get_image(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="50" height="50" />', obj.foto.url)
        return "-"
    get_image.short_description = 'Foto'


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'codigo_unico_doctor', 'ruc', 'email', 'activo')
    list_filter = ('especialidad', 'activo')
    search_fields = ('nombres', 'apellidos', 'codigo_unico_doctor', 'ruc')


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cedula_ecuatoriana', 'cargo', 'sueldo', 'activo')
    search_fields = ('nombres', 'apellidos', 'cedula_ecuatoriana')
    list_filter = ('cargo', 'activo')


@admin.register(TipoMedicamento)
class TipoMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(MarcaMedicamento)
class MarcaMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'marca_medicamento', 'precio', 'cantidad', 'comercial', 'activo')
    search_fields = ('nombre',)
    list_filter = ('tipo', 'marca_medicamento', 'comercial', 'activo')


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'activo')
    search_fields = ('codigo', 'descripcion')
    list_filter = ('activo',)


@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(GastoMensual)
class GastoMensualAdmin(admin.ModelAdmin):
    list_display = ('tipo_gasto', 'valor', 'fecha')
    search_fields = ('tipo_gasto__nombre',)
    list_filter = ('tipo_gasto', 'fecha')


@admin.register(FotoPaciente)
class FotoPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha_subida', 'descripcion')
    search_fields = ('paciente__nombres', 'paciente__apellidos')
    list_filter = ('fecha_subida', 'paciente')
