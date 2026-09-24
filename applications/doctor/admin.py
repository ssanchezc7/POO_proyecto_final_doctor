from django.contrib import admin
from .models import (
    HorarioAtencion,
    CitaMedica,
    Atencion,
    DetalleAtencion,
    ServiciosAdicionales,
    Pago,
    DetallePago
)


@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "hora_inicio", "hora_fin", "activo")
    list_filter = ("dia_semana", "activo")



@admin.register(CitaMedica)
class CitaMedicaAdmin(admin.ModelAdmin):
    list_display = ("paciente","fecha", "hora_cita", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("paciente__nombres", "paciente__apellidos", "doctor__nombres", "doctor__apellidos")


class DetalleAtencionInline(admin.TabularInline):
    model = DetalleAtencion
    extra = 0


@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ("paciente", "fecha_atencion", "es_control")
    list_filter = ("fecha_atencion", "es_control")
    search_fields = ("paciente__nombres", "paciente__apellidos")
    inlines = [DetalleAtencionInline]


@admin.register(ServiciosAdicionales)
class ServiciosAdicionalesAdmin(admin.ModelAdmin):
    list_display = ("nombre_servicio", "costo_servicio", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre_servicio",)


class DetallePagoInline(admin.TabularInline):
    model = DetallePago
    extra = 0


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "atencion", "monto_total", "estado", "metodo_pago", "fecha_pago", "fecha_creacion")
    list_filter = ("estado", "metodo_pago", "fecha_creacion")
    search_fields = ("atencion__paciente__nombres", "atencion__paciente__apellidos", "nombre_pagador")
    inlines = [DetallePagoInline]


@admin.register(DetallePago)
class DetallePagoAdmin(admin.ModelAdmin):
    list_display = (
        "pago", "servicio_adicional", "cantidad", "precio_unitario", "aplica_seguro", "valor_seguro", "subtotal"
    )
    list_filter = ("aplica_seguro", "servicio_adicional")
    search_fields = ("pago__atencion__paciente__nombres", "pago__atencion__paciente__apellidos")

