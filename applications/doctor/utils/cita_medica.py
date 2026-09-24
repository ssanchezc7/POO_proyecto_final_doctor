from django.db import models
from datetime import datetime, timedelta, date
from calendar import monthrange
from collections import defaultdict




class EstadoCitaChoices(models.TextChoices):
    DISPONIBLE = 'disponible', 'Disponible'
    OCUPADO = 'ocupado', 'Ocupado'
    ATENDIDO = 'atendido', 'Atendido'



# def generar_calendario_disponibilidad_json(doctor, anio, mes):
#     """
#     Devuelve un diccionario serializable en JSON que representa el calendario mensual
#     de disponibilidad del doctor, con franjas horarias y su estado.
#     """
#     calendario = defaultdict(list)
#     dias_mes = monthrange(anio, mes)[1]
#     primer_dia = date(anio, mes, 1)
#     ultimo_dia = date(anio, mes, dias_mes)
#
#     citas = CitaMedica.objects.filter(
#         doctor=doctor,
#         fecha__range=(primer_dia, ultimo_dia)
#     )
#     citas_map = {(cita.fecha, cita.hora_cita): cita.estado for cita in citas}
#     horarios = HorarioAtencion.objects.filter(doctor=doctor, activo=True)
#
#     for dia in range(1, dias_mes + 1):
#         fecha_actual = date(anio, mes, dia)
#         dia_semana = fecha_actual.strftime("%A").lower()
#
#         for horario in horarios:
#             if horario.dia_semana.lower() == dia_semana:
#                 hora = horario.hora_inicio
#                 while hora < horario.hora_fin:
#                     if horario.intervalo_desde and horario.intervalo_hasta:
#                         if horario.intervalo_desde <= hora < horario.intervalo_hasta:
#                             hora = (datetime.combine(date.today(), horario.intervalo_hasta) + timedelta(minutes=doctor.duracion_cita)).time()
#                             continue
#
#                     estado = "disponible"
#                     cita_estado = citas_map.get((fecha_actual, hora))
#                     if cita_estado == 'A':
#                         estado = "atendida"
#                     elif cita_estado:
#                         estado = "ocupada"
#
#                     calendario[str(fecha_actual)].append({
#                         "hora": hora.strftime("%H:%M"),
#                         "estado": estado,
#                     })
#
#                     dt = datetime.combine(fecha_actual, hora) + timedelta(minutes=doctor.duracion_cita)
#                     hora = dt.time()
#
#     return dict(calendario)
