from decimal import Decimal

from django.utils import timezone
from django.db import models
from applications.doctor.utils.cita_medica import EstadoCitaChoices
from applications.doctor.utils.doctor import DiaSemanaChoices
from applications.doctor.utils.pago import MetodoPagoChoices, EstadoPagoChoices

"""
    Modelo Patient: Representa los pacientes registrados en el sistema médico.
"""

class HorarioAtencion(models.Model):

    # Día de la semana (ej: lunes, martes...)
    dia_semana = models.CharField(
        max_length=10,
        choices=DiaSemanaChoices.choices,
        verbose_name="Día de la Semana"
    )

    # Rango principal de atención (ej. 08:00 a 17:00)
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")

    # Pausa para almuerzo u otro intervalo
    intervalo_desde = models.TimeField(verbose_name="Intervalo desde", null=True, blank=True)
    intervalo_hasta = models.TimeField(verbose_name="Intervalo hasta", null=True, blank=True)

    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        horario = f"{self.get_dia_semana_display()}: {self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"
        if self.intervalo_desde and self.intervalo_hasta:
            horario += f" (Pausa: {self.intervalo_desde.strftime('%H:%M')} - {self.intervalo_hasta.strftime('%H:%M')})"
        return horario

    class Meta:
        verbose_name = "Horario de Atención"
        verbose_name_plural = "Horarios de Atención"
        unique_together = ('dia_semana', 'hora_inicio', 'hora_fin')  # Evita duplicados exactos

class CitaMedica(models.Model):
    paciente = models.ForeignKey('core.Paciente', on_delete=models.CASCADE, verbose_name="Paciente", related_name="citas")
    doctor = models.ForeignKey('core.Doctor', on_delete=models.CASCADE, verbose_name="Doctor", related_name="citas_medicas")
    fecha = models.DateField(verbose_name="Fecha de la Cita")
    hora_cita = models.TimeField(verbose_name="Hora de la Cita")

    estado = models.CharField(
        max_length=10,
        choices=EstadoCitaChoices.choices,
        verbose_name="Estado de la Cita",
        default=EstadoCitaChoices.DISPONIBLE
    )

    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)

    def __str__(self):
        return f"{self.paciente.nombre_completo} - {self.fecha} {self.hora_cita}"

    class Meta:
        ordering = ['fecha', 'hora_cita']
        indexes = [
            models.Index(fields=['fecha', 'hora_cita'], name='idx_fecha_hora'),
        ]
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        unique_together = ('doctor', 'fecha', 'hora_cita')  # Previene duplicidad por doctor

class Atencion(models.Model):
    # Paciente que recibe esta atención médica
    paciente = models.ForeignKey(
        'core.Paciente',
        on_delete=models.PROTECT,
        verbose_name="Paciente",
        related_name="atenciones",
        help_text="Paciente que recibe esta atención médica."
    )

    # Fecha y hora en que se realizó la atención
    fecha_atencion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Atención",
        help_text="Fecha y hora en que se registró la atención."
    )
    # Signos vitales
    presion_arterial = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Presión Arterial",
        help_text="Ejemplo: 120/80 mmHg."
    )
    pulso = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Pulso (ppm)",
        help_text="Pulsaciones por minuto."
    )
    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Temperatura (°C)",
        help_text="Temperatura corporal en grados Celsius."
    )
    frecuencia_respiratoria = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Frecuencia Respiratoria (rpm)",
        help_text="Respiraciones por minuto."
    )
    saturacion_oxigeno = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Saturación de Oxígeno (%)",
        help_text="Porcentaje de oxígeno en sangre."
    )
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso (kg)",
        help_text="Peso del paciente en kilogramos."
    )
    altura = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Altura (m)",
        help_text="Altura del paciente en metros."
    )

    # Motivo y contenido de la atención
    motivo_consulta = models.TextField(
        verbose_name="Motivo de Consulta",
        help_text="Razón principal por la que el paciente acude a consulta."
    )
    sintomas = models.TextField(
        verbose_name="Síntomas",
        help_text="Síntomas que presenta el paciente."
    )
    tratamiento = models.TextField(
        verbose_name="Plan de Tratamiento",
        help_text="Indicaciones o receta entregada al paciente."
    )
    diagnostico = models.ManyToManyField(
        'core.Diagnostico',
        verbose_name="Diagnósticos",
        related_name="atenciones",
        help_text="Diagnósticos clínicos asociados a esta atención."
    )
    examen_fisico = models.TextField(
        null=True,
        blank=True,
        verbose_name="Examen Físico",
        help_text="Descripción de hallazgos del examen físico."
    )
    examenes_enviados = models.TextField(
        null=True,
        blank=True,
        verbose_name="Exámenes Solicitados",
        help_text="Exámenes que se han solicitado al paciente."
    )
    comentario_adicional = models.TextField(
        null=True,
        blank=True,
        verbose_name="Comentario Adicional",
        help_text="Observaciones adicionales del profesional de salud."
    )
    es_control = models.BooleanField(
        default=False,
        verbose_name="¿Es consulta de control?",
        help_text="Marca si esta atención es parte de un seguimiento."
    )

    class Meta:
        ordering = ['-fecha_atencion']
        verbose_name = "Atención Médica"
        verbose_name_plural = "Atenciones Médicas"

    def __str__(self):
        return f"Atención de {self.paciente} el {self.fecha_atencion.strftime('%Y-%m-%d %H:%M')}"

    @property
    def calcular_imc(self):
        """Calcula el Índice de Masa Corporal (IMC) basado en el peso y la altura."""
        if self.peso and self.altura and self.altura > 0:
            return round(float(self.peso) / (float(self.altura) ** 2), 2)
        return None

    @property
    def get_diagnosticos(self):
        return " - ".join([d.descripcion for d in self.diagnostico.all().order_by('descripcion')])


class DetalleAtencion(models.Model):
    atencion = models.ForeignKey(
        Atencion,
        on_delete=models.CASCADE,
        verbose_name="Atención Médica",
        related_name="detalles",
        help_text="Atención médica asociada a este detalle."
    )
    medicamento = models.ForeignKey(
        'core.Medicamento',
        on_delete=models.PROTECT,
        verbose_name="Medicamento",
        related_name="prescripciones",
        help_text="Medicamento recetado al paciente."
    )
    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
        help_text="Unidades del medicamento recetadas."
    )
    prescripcion = models.TextField(
        verbose_name="Prescripción",
        help_text="Instrucciones para tomar el medicamento."
    )
    duracion_tratamiento = models.PositiveIntegerField(
        verbose_name="Duración del Tratamiento (días)",
        null=True,
        blank=True,
        help_text="Cantidad de días de tratamiento estimado."
    )
    frecuencia_diaria = models.PositiveIntegerField(
        verbose_name="Frecuencia Diaria (veces por día)",
        null=True,
        blank=True,
        help_text="Cuántas veces al día debe tomar el medicamento."
    )

    class Meta:
        ordering = ['atencion']
        verbose_name = "Detalle de Atención"
        verbose_name_plural = "Detalles de Atención"

    def __str__(self):
        return f"{self.medicamento} para {self.atencion.paciente}"

# Modelo que representa un servicio adicional ofrecido durante una atención médica.
# Puede incluir exámenes, procedimientos, o cualquier otro servicio.
class ServiciosAdicionales(models.Model):
    # Nombre del servicio (ej. Radiografía, Laboratorio, Procedimiento menor, etc.)
    nombre_servicio = models.CharField(
        max_length=255,
        verbose_name="Nombre del Servicio",
        help_text="Ejemplo: Radiografía, Laboratorio clínico, Procedimiento menor."
    )

    # Costo unitario del servicio adicional
    costo_servicio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo del Servicio",
        help_text="Costo unitario del servicio en dólares. Ejemplo: 25.00"
    )

    # Descripción opcional del servicio adicional
    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción del Servicio",
        help_text="Descripción opcional del servicio. Ejemplo: Examen de sangre de rutina."
    )

    # Indica si el servicio está activo o no
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Marca si el servicio adicional está disponible para agendar o prescribir."
    )

    class Meta:
        ordering = ['nombre_servicio']
        verbose_name = "Servicio Adicional"
        verbose_name_plural = "Servicios Adicionales"

    def __str__(self):
        return self.nombre_servicio

# Pago de atencion y servicios varios
class Pago(models.Model):
    # Relación con la atención médica (opcional para servicios independientes)
    atencion = models.ForeignKey(Atencion, on_delete=models.PROTECT,
                                 verbose_name="Atención", related_name="pagos",
                                 null=True, blank=True)

    # Información del pago
    metodo_pago = models.CharField(max_length=20, choices=MetodoPagoChoices.choices,
                                   verbose_name="Método de Pago")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      verbose_name="Monto Total")
    estado = models.CharField(max_length=20, choices=EstadoPagoChoices.choices,
                              default=EstadoPagoChoices.PENDIENTE, verbose_name="Estado")

    # Fechas
    fecha_pago = models.DateTimeField(verbose_name="Fecha de Pago", null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    # Información del pagador (opcional)
    nombre_pagador = models.CharField(max_length=100, verbose_name="Nombre del Pagador",
                                      blank=True, null=True)

    # Para pagos digitales
    referencia_externa = models.CharField(max_length=100, verbose_name="Referencia Externa",
                                          blank=True, null=True,
                                          help_text="ID de transacción PayPal, etc.")

    # Evidencia del pago (solo para pagos no efectivo)
    evidencia_pago = models.ImageField(upload_to='doctor/evidencia_pagos/', verbose_name="Evidencia de Pago",
                                       blank=True, null=True,
                                       help_text="Captura de pantalla o comprobante del pago")

    # Notas adicionales
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)

    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return f"Pago {self.id} - {self.atencion} - {self.monto_total}"

    def save(self, *args, **kwargs):
        # Auto-asignar fecha de pago cuando el estado cambia a 'pagado'
        if self.estado == 'pagado' and not self.fecha_pago:
            self.fecha_pago = timezone.now()
        self.clean()
        super().save(*args, **kwargs)

    def recalcular_total(self):
        """Recalcula el monto total basado en todos los detalles"""
        from django.db.models import Sum
        total = self.detalles.aggregate(
            total=Sum('subtotal')
        )['total'] or Decimal('0.00')
        self.monto_total = total
        return self.monto_total

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

class DetallePago(models.Model):
    # Relación con el pago principal
    pago = models.ForeignKey(
        'Pago',
        on_delete=models.CASCADE,
        verbose_name="Pago",
        related_name="detalles",
        help_text="Pago al que corresponde este detalle de cobro."
    )

    # Servicio facturado
    servicio_adicional = models.ForeignKey(
        'ServiciosAdicionales',
        on_delete=models.PROTECT,
        verbose_name="Servicio",
        related_name="detalles_pago",
        help_text="Servicio adicional cobrado (ej. Radiografía, Laboratorio)."
    )

    # Cantidad del servicio prestado
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad",
        help_text="Cantidad del servicio facturado (ej. 1 examen, 2 procedimientos, etc.)."
    )

    # Precio normal sin seguro
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Unitario",
        help_text="Precio normal por unidad del servicio, sin considerar seguros."
    )

    # Subtotal calculado (automático)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal",
        editable=False,
        help_text="Subtotal calculado automáticamente, considerando seguro y descuento."
    )

    # Porcentaje de descuento aplicado
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Descuento %",
        help_text="Descuento aplicado sobre el precio base. Ejemplo: 10 para 10%."
    )

    # Indica si se aplica seguro
    aplica_seguro = models.BooleanField(
        default=False,
        verbose_name="Aplica Seguro",
        help_text="Marca si el servicio tiene cobertura por seguro médico."
    )

    # Valor real que cubre el seguro (reemplaza precio_unitario)
    valor_seguro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Cubierto por Seguro",
        help_text="Valor real cubierto por el seguro. Se usará en lugar del precio normal si se aplica seguro."
    )

    # Descripción del seguro utilizado
    descripcion_seguro = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción del Seguro",
        help_text="Nombre del seguro utilizado. Ejemplo: Saludsa Nivel 2."
    )

    def save(self, *args, **kwargs):
        # Determinar precio base (seguro o normal)
        precio_base = self.valor_seguro if self.aplica_seguro and self.valor_seguro is not None else self.precio_unitario

        # Aplicar descuento
        descuento = (self.descuento_porcentaje / Decimal(100)) * precio_base
        precio_con_descuento = precio_base - descuento

        # Calcular subtotal final
        self.subtotal = round(precio_con_descuento * self.cantidad, 2)

        super().save(*args, **kwargs)
        # Nota: El signal post_save se encargará de actualizar el total del pago

    def actualizar_total_pago(self):
        """Actualiza el monto total del pago basado en todos los detalles (DEPRECATED)"""
        # Este método ya no se usa directamente, las signals se encargan del recálculo
        total = self.pago.detalles.aggregate(
            total=models.Sum('subtotal')
        )['total'] or 0
        self.pago.monto_total = total
        self.pago.save()

    def __str__(self):
        return f"{self.servicio_adicional} - Cantidad: {self.cantidad} - Subtotal: {self.subtotal}"

    class Meta:
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"