import json
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone

from applications.core.models import Paciente, Medicamento, Diagnostico
from applications.doctor.forms.atencion import AtencionForm
from applications.doctor.models import Atencion, DetalleAtencion, Pago, DetallePago, ServiciosAdicionales
from applications.doctor.utils.pago import MetodoPagoChoices, EstadoPagoChoices
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, \
    PermissionMixin, UpdateViewMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from proy_clinico.util import save_audit


def obtener_servicio_consulta_medica():
    """
    Obtiene o crea el servicio adicional de 'Consulta Médica' que se usará
    para crear automáticamente el pago de las atenciones médicas.
    """
    servicio, created = ServiciosAdicionales.objects.get_or_create(
        nombre_servicio="Consulta Médica",
        defaults={
            'costo_servicio': Decimal('25.00'),  # Precio por defecto de consulta
            'descripcion': 'Consulta médica general - Servicio creado automáticamente',
            'activo': True
        }
    )

    if created:
        print(f"✅ Servicio 'Consulta Médica' creado automáticamente con costo ${servicio.costo_servicio}")

    return servicio


def obtener_servicio_medicamento(medicamento):
    """
    Obtiene o crea un servicio adicional para un medicamento específico.
    
    Args:
        medicamento (Medicamento): El medicamento para el cual crear/obtener el servicio
        
    Returns:
        ServiciosAdicionales: El servicio adicional para el medicamento
    """
    servicio_nombre = f"Medicamento: {medicamento.nombre}"
    
    servicio, created = ServiciosAdicionales.objects.get_or_create(
        nombre_servicio=servicio_nombre,
        defaults={
            'costo_servicio': medicamento.precio,
            'descripcion': f'Medicamento recetado: {medicamento.nombre} - {medicamento.concentracion or ""} - {medicamento.get_via_administracion_display()}',
            'activo': True
        }
    )
    
    # Si el servicio ya existía, actualizamos el precio por si cambió
    if not created and servicio.costo_servicio != medicamento.precio:
        servicio.costo_servicio = medicamento.precio
        servicio.save()
        print(f"🔄 Precio del servicio '{servicio_nombre}' actualizado a ${medicamento.precio}")
    
    if created:
        print(f"✅ Servicio para medicamento '{medicamento.nombre}' creado automáticamente con costo ${medicamento.precio}")
    
    return servicio


def crear_pago_automatico(atencion):
    """
    Crea automáticamente un pago pendiente para la atención médica proporcionada,
    incluyendo todos los medicamentos recetados como detalles del pago.

    Args:
        atencion (Atencion): La instancia de atención médica para la cual crear el pago

    Returns:
        Pago: La instancia del pago creado
    """
    try:
        with transaction.atomic():
            # Obtener el servicio de consulta médica
            servicio_consulta = obtener_servicio_consulta_medica()

            # Crear el pago principal
            pago = Pago.objects.create(
                atencion=atencion,
                metodo_pago=MetodoPagoChoices.EFECTIVO,  # Por defecto efectivo, se puede cambiar luego
                monto_total=Decimal('0.00'),  # Se calculará automáticamente en el DetallePago
                estado=EstadoPagoChoices.PENDIENTE,
                nombre_pagador=f"{atencion.paciente.nombres} {atencion.paciente.apellidos}",
                observaciones=f"Pago generado automáticamente para atención del {atencion.fecha_atencion.strftime('%d/%m/%Y %H:%M')} - Incluye consulta médica y medicamentos recetados"
            )

            # Crear el detalle del pago con el servicio de consulta médica
            DetallePago.objects.create(
                pago=pago,
                servicio_adicional=servicio_consulta,
                cantidad=1,
                precio_unitario=servicio_consulta.costo_servicio,
                descuento_porcentaje=Decimal('0.00'),
                aplica_seguro=False
            )
            
            # Obtener todos los medicamentos recetados en esta atención
            medicamentos_recetados = atencion.detalles.all()
            
            if medicamentos_recetados.exists():
                print(f"📋 Agregando {medicamentos_recetados.count()} medicamentos recetados al pago...")
                
                for detalle_atencion in medicamentos_recetados:
                    # Obtener o crear el servicio adicional para este medicamento
                    servicio_medicamento = obtener_servicio_medicamento(detalle_atencion.medicamento)
                    
                    # Crear el detalle de pago para este medicamento
                    DetallePago.objects.create(
                        pago=pago,
                        servicio_adicional=servicio_medicamento,
                        cantidad=detalle_atencion.cantidad,
                        precio_unitario=detalle_atencion.medicamento.precio,
                        descuento_porcentaje=Decimal('0.00'),
                        aplica_seguro=False
                    )
                    
                    print(f"💊 Agregado: {detalle_atencion.medicamento.nombre} x{detalle_atencion.cantidad} - ${detalle_atencion.medicamento.precio} c/u")
            else:
                print("ℹ️ No hay medicamentos recetados en esta atención")
            
            # Recargar el pago para obtener el monto total actualizado
            pago.refresh_from_db()
            
            # Mostrar resumen del pago creado
            total_detalles = pago.detalles.count()
            print(f"💰 Pago automático creado - ID: {pago.id}")
            print(f"   📊 Total de detalles: {total_detalles}")
            print(f"   💵 Monto total: ${pago.monto_total}")
            print(f"   🏥 Consulta médica: ${servicio_consulta.costo_servicio}")
            
            if medicamentos_recetados.exists():
                monto_medicamentos = pago.monto_total - servicio_consulta.costo_servicio
                print(f"   💊 Medicamentos: ${monto_medicamentos}")

            return pago

    except Exception as e:
        print(f"❌ Error al crear pago automático: {str(e)}")
        raise e


class AtencionListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'doctor/atenciones/list.html'
    model = Atencion
    context_object_name = 'atenciones'
    permission_required = 'view_atencion'

    def get_queryset(self):
        q1 = self.request.GET.get('q')

        if q1 is not None:
            self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
            self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)
            self.query.add(Q(motivo_consulta__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('-fecha_atencion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('doctor:atencion_create')

        return context


class AtencionCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Atencion
    template_name = 'doctor/atenciones/form.html'
    form_class = AtencionForm
    success_url = reverse_lazy('doctor:atencion_list')
    permission_required = 'add_atencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Atención'
        context['back_url'] = self.success_url
        context['diagnosticos'] = Diagnostico.objects.filter(activo=True)
        context['medicamentos'] = (Medicamento.objects.filter(activo=True)
            .select_related('tipo', 'marca_medicamento')
            .only('id', 'nombre', 'concentracion', 'via_administracion',
                  'precio', 'cantidad', 'tipo__nombre', 'marca_medicamento__nombre'
                  ).order_by('nombre'))

        context['paciente_json'] = 'null'
        context['medicamentos_json'] = '[]'  # Array vacío
        context['modo_edicion'] = False
        return context

    def post(self, request, *args, **kwargs):
        # Convertir el cuerpo de la solicitud a un diccionario Python
        data = json.loads(request.body)

        # Extraer los objetos anidados
        signos_vitales = data.get('signosVitales', {})
        evaluacion_clinica = data.get('evaluacionClinica', {})
        plan_terapeutico = data.get('planTerapeutico', {})
        medicamentos = data.get('medicamentos', [])

        # Conversiones simples (el frontend ya validó)
        def to_int(value):
            return int(value) if value is not None and value != '' else None

        def to_decimal(value):
            return Decimal(str(value)) if value is not None and value != '' else None

        try:
            with transaction.atomic():
                # Crear la instancia del modelo Atencion
                atencion = Atencion.objects.create(
                    # Datos básicos
                    paciente_id=to_int(data.get('paciente')),

                    # Signos vitales
                    presion_arterial=signos_vitales.get('presionArterial'),
                    pulso=to_int(signos_vitales.get('pulso')),
                    temperatura=to_decimal(signos_vitales.get('temperatura')),
                    frecuencia_respiratoria=to_int(signos_vitales.get('frecuenciaRespiratoria')),
                    saturacion_oxigeno=to_decimal(signos_vitales.get('saturacionOxigeno')),
                    peso=to_decimal(signos_vitales.get('peso')),
                    altura=to_decimal(signos_vitales.get('altura')),
                    es_control=bool(signos_vitales.get('consultaControl', False)),

                    # Evaluación clínica
                    motivo_consulta=evaluacion_clinica.get('motivoConsulta', ''),
                    sintomas=evaluacion_clinica.get('sintomas', ''),
                    examen_fisico=evaluacion_clinica.get('examenFisico'),

                    # Plan terapéutico
                    tratamiento=plan_terapeutico.get('tratamiento', ''),
                    examenes_enviados=plan_terapeutico.get('examenesEnviados'),
                    comentario_adicional=plan_terapeutico.get('comentarioAdicional'),

                    # Fecha automática
                    fecha_atencion=timezone.now()
                )

                # Procesar diagnósticos
                diagnostico_ids = evaluacion_clinica.get('diagnostico', [])
                if diagnostico_ids:
                    diagnosticos = Diagnostico.objects.filter(id__in=diagnostico_ids)
                    atencion.diagnostico.set(diagnosticos)

                # Procesar medicamentos
                for medicamento in medicamentos:
                    DetalleAtencion.objects.create(
                        atencion=atencion,
                        medicamento_id=to_int(medicamento.get('id')),
                        cantidad=to_int(medicamento.get('cantidad')),
                        prescripcion=medicamento.get('prescripcion'),
                        duracion_tratamiento=to_int(medicamento.get('duracion')),
                        frecuencia_diaria=to_int(medicamento.get('frecuencia'))
                    )

                # Guardar auditoría
                save_audit(request, atencion, "ADICION")

                # 🆕 CREAR PAGO AUTOMÁTICO
                try:
                    pago_automatico = crear_pago_automatico(atencion)
                    print(f"✅ Pago automático creado exitosamente - ID: {pago_automatico.id}")
                    messages.success(request, f"Atención médica registrada exitosamente. Se ha creado automáticamente el pago #{pago_automatico.id} por ${pago_automatico.monto_total}")
                except Exception as e:
                    print(f"⚠️ Error al crear pago automático: {str(e)}")
                    messages.warning(request, f"Atención médica registrada, pero hubo un problema al crear el pago automático: {str(e)}")

                # Mensaje de éxito principal
                messages.success(request, f"Éxito al registrar la atención médica #{atencion.id}")

                # Respuesta exitosa
                return JsonResponse({
                    "msg": "Atención médica registrada exitosamente",
                    "id": atencion.id,
                    "fecha": atencion.fecha_atencion.strftime('%Y-%m-%d %H:%M:%S'),
                    "paciente": str(atencion.paciente)
                }, status=200)

        except Exception as e:
            messages.error(request, f"Error al registrar la atención médica")
            return JsonResponse({
                "msg": f"Error al registrar la atención médica: {str(e)}"
            }, status=500)


class AtencionUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Atencion
    template_name = 'doctor/atenciones/form.html'
    form_class = AtencionForm
    success_url = reverse_lazy('doctor:atencion_list')
    permission_required = 'change_atencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar Atención'
        context['back_url'] = self.success_url

        # Contextos iguales al CreateView
        context['diagnosticos'] = Diagnostico.objects.filter(activo=True)
        context['medicamentos'] = (Medicamento.objects.filter(activo=True)
                                   .select_related('tipo', 'marca_medicamento')
                                   .only('id', 'nombre', 'concentracion', 'via_administracion',
                                         'precio', 'cantidad', 'tipo__nombre', 'marca_medicamento__nombre'
                                         ).order_by('nombre'))

        # Contexto específico para el update: detalles de atención actual
        atencion = self.get_object()

        # Obtener contexto completo del paciente para edición
        contexto_paciente = obtener_contexto_paciente(atencion.paciente.id)
        context['paciente_json'] = contexto_paciente['paciente_json']
        context['paciente_data'] = contexto_paciente['paciente_data']
        context['modo_edicion'] = True

        # Datos de la atención actual para usar directamente en el HTML
        context['atencion'] = atencion
        print("atenciones")
        print(atencion.temperatura)
        print(type(atencion.temperatura))
        # Solo los medicamentos para cargar dinámicamente con JavaScript
        medicamentos = []
        for detalle in atencion.detalles.select_related('medicamento').all():
            medicamento_dict = {
                'id': detalle.medicamento.id,
                'nombre': detalle.medicamento.nombre,
                'concentracion': detalle.medicamento.concentracion,
                'via_administracion': detalle.medicamento.via_administracion,
                'cantidad': detalle.cantidad,
                'prescripcion': detalle.prescripcion,
                'duracion': detalle.duracion_tratamiento,
                'frecuencia': detalle.frecuencia_diaria,
                'precio': float(detalle.medicamento.precio) if detalle.medicamento.precio else 0
            }
            medicamentos.append(medicamento_dict)

        # Solo los medicamentos en JSON para JavaScript
        context['medicamentos_json'] = json.dumps(medicamentos)

        return context

    def post(self, request, *args, **kwargs):
        # Obtener la instancia actual que se va a actualizar
        atencion = self.get_object()

        # Convertir el cuerpo de la solicitud a un diccionario Python
        data = json.loads(request.body)

        # Extraer los objetos anidados
        signos_vitales = data.get('signosVitales', {})
        evaluacion_clinica = data.get('evaluacionClinica', {})
        plan_terapeutico = data.get('planTerapeutico', {})
        medicamentos = data.get('medicamentos', [])

        # Conversiones simples (el frontend ya validó)
        def to_int(value):
            return int(value) if value is not None and value != '' else None

        def to_decimal(value):
            return Decimal(str(value)) if value is not None and value != '' else None

        try:
            with transaction.atomic():
                # Actualizar la instancia existente de Atencion
                atencion.paciente_id = to_int(data.get('paciente'))

                # Signos vitales
                atencion.presion_arterial = signos_vitales.get('presionArterial')
                atencion.pulso = to_int(signos_vitales.get('pulso'))
                atencion.temperatura = to_decimal(signos_vitales.get('temperatura'))
                atencion.frecuencia_respiratoria = to_int(signos_vitales.get('frecuenciaRespiratoria'))
                atencion.saturacion_oxigeno = to_decimal(signos_vitales.get('saturacionOxigeno'))
                atencion.peso = to_decimal(signos_vitales.get('peso'))
                atencion.altura = to_decimal(signos_vitales.get('altura'))
                atencion.es_control = bool(signos_vitales.get('consultaControl', False))

                # Evaluación clínica
                atencion.motivo_consulta = evaluacion_clinica.get('motivoConsulta', '')
                atencion.sintomas = evaluacion_clinica.get('sintomas', '')
                atencion.examen_fisico = evaluacion_clinica.get('examenFisico')

                # Plan terapéutico
                atencion.tratamiento = plan_terapeutico.get('tratamiento', '')
                atencion.examenes_enviados = plan_terapeutico.get('examenesEnviados')
                atencion.comentario_adicional = plan_terapeutico.get('comentarioAdicional')

                # Guardar los cambios en la atención
                atencion.save()

                # Procesar diagnósticos
                diagnostico_ids = evaluacion_clinica.get('diagnostico', [])
                if diagnostico_ids:
                    diagnosticos = Diagnostico.objects.filter(id__in=diagnostico_ids)
                    atencion.diagnostico.set(diagnosticos)
                else:
                    # Si no hay diagnósticos, limpiar la relación
                    atencion.diagnostico.clear()

                # Procesar medicamentos: borrar existentes y crear nuevos
                DetalleAtencion.objects.filter(atencion=atencion).delete()

                for medicamento in medicamentos:
                    DetalleAtencion.objects.create(
                        atencion=atencion,
                        medicamento_id=to_int(medicamento.get('id')),
                        cantidad=to_int(medicamento.get('cantidad')),
                        prescripcion=medicamento.get('prescripcion'),
                        duracion_tratamiento=to_int(medicamento.get('duracion')),
                        frecuencia_diaria=to_int(medicamento.get('frecuencia'))
                    )

                # Guardar auditoría para modificación
                save_audit(request, atencion, "MODIFICACION")

                # Mensaje de éxito
                messages.success(request, f"Éxito al actualizar la atención médica #{atencion.id}")
                
                # Verificar si existe pago para esta atención
                pagos_existentes = atencion.pagos.count()
                if pagos_existentes == 0:
                    messages.info(request, "Esta atención no tiene pagos asociados. Considere crear uno manualmente si es necesario.")

                # Respuesta exitosa
                return JsonResponse({
                    "msg": "Atención médica actualizada exitosamente",
                    "id": atencion.id,
                    "fecha": atencion.fecha_atencion.strftime('%Y-%m-%d %H:%M:%S'),
                    "paciente": str(atencion.paciente)
                }, status=200)

        except Exception as e:
            messages.error(request, f"Error al actualizar la atención médica")
            return JsonResponse({
                "msg": f"Error al actualizar la atención médica: {str(e)}"
            }, status=500)


class AtencionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Atencion
    template_name = 'core/delete.html'
    success_url = reverse_lazy('doctor:atencion_list')
    permission_required = 'delete_atencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Atención'
        context['description'] = f"¿Desea eliminar la atención de: {self.object.paciente}?"
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        paciente_nombre = self.object.paciente
        response = super().form_valid(form)
        messages.success(self.request, f"Éxito al eliminar lógicamente la atención de {paciente_nombre}.")
        return response


def obtener_contexto_paciente(id_paciente):
    try:
        paciente = Paciente.objects.select_related('tipo_sangre').prefetch_related(
            'atenciones__diagnostico',
            'atenciones__detalles__medicamento'
        ).get(id=id_paciente, activo=True)

        edad = paciente.edad
        # Obtener atenciones anteriores (últimas 10)
        atenciones = []
        for atencion in paciente.atenciones.all()[:10]:
            # Obtener prescripciones/detalles de esta atención
            detalles = []
            for detalle in atencion.detalles.all():
                detalle_dict = {
                    'medicamento': detalle.medicamento.nombre if detalle.medicamento else '',
                    'cantidad': detalle.cantidad,
                    'prescripcion': detalle.prescripcion,
                    'duracion_tratamiento': detalle.duracion_tratamiento,
                    'frecuencia_diaria': detalle.frecuencia_diaria,
                }
                detalles.append(detalle_dict)

            # Obtener diagnósticos
            diagnosticos = [d.descripcion for d in atencion.diagnostico.all()]

            # Determinar tipo de consulta
            tipo_consulta = "Chequeo"
            if atencion.es_control:
                tipo_consulta = "Control"
            elif "urgencia" in atencion.motivo_consulta.lower() or "dolor" in atencion.motivo_consulta.lower():
                tipo_consulta = "Urgencia"

            atencion_dict = {
                'id': atencion.id,
                'fecha_atencion': atencion.fecha_atencion.isoformat(),
                'tipo_consulta': tipo_consulta,

                # Signos vitales
                'presion_arterial': atencion.presion_arterial,
                'pulso': atencion.pulso,
                'temperatura': float(atencion.temperatura) if atencion.temperatura else '',
                'frecuencia_respiratoria': atencion.frecuencia_respiratoria,
                'saturacion_oxigeno': float(atencion.saturacion_oxigeno) if atencion.saturacion_oxigeno else '',
                'peso': float(atencion.peso) if atencion.peso else '',
                'altura': float(atencion.altura) if atencion.altura else '',
                'imc': atencion.calcular_imc,

                # Contenido de la atención
                'motivo_consulta': atencion.motivo_consulta,
                'sintomas': atencion.sintomas,
                'tratamiento': atencion.tratamiento,
                'diagnosticos': diagnosticos,
                'examen_fisico': atencion.examen_fisico,
                'examenes_enviados': atencion.examenes_enviados,
                'comentario_adicional': atencion.comentario_adicional,
                'es_control': atencion.es_control,

                # Prescripciones
                'prescripciones': detalles
            }
            atenciones.append(atencion_dict)

        # Crear diccionario del paciente
        paciente_data = {
            'id': paciente.id,
            'nombres': paciente.nombres,
            'apellidos': paciente.apellidos,
            'cedula_ecuatoriana': paciente.cedula_ecuatoriana,
            'dni': paciente.dni,
            'fecha_nacimiento': paciente.fecha_nacimiento.isoformat() if paciente.fecha_nacimiento else '',
            'edad': edad,
            'telefono': paciente.telefono,
            'email': paciente.email,
            'sexo': paciente.sexo,
            'estado_civil': paciente.estado_civil,
            'direccion': paciente.direccion,
            'latitud': float(paciente.latitud) if paciente.latitud else '',
            'longitud': float(paciente.longitud) if paciente.longitud else '',
            'tipo_sangre': paciente.tipo_sangre.tipo if paciente.tipo_sangre else '',
            'foto_url': paciente.get_image,

            # Historia clínica
            'antecedentes_personales': paciente.antecedentes_personales,
            'antecedentes_quirurgicos': paciente.antecedentes_quirurgicos,
            'antecedentes_familiares': paciente.antecedentes_familiares,
            'alergias': paciente.alergias,
            'medicamentos_actuales': paciente.medicamentos_actuales,
            'habitos_toxicos': paciente.habitos_toxicos,
            'vacunas': paciente.vacunas,
            'antecedentes_gineco_obstetricos': paciente.antecedentes_gineco_obstetricos,

            # Atenciones anteriores
            'atenciones': atenciones,
            'total_atenciones': paciente.atenciones.count()
        }

        return {
            'paciente_data': paciente_data,
            'paciente_json': json.dumps(paciente_data)
        }

    except Paciente.DoesNotExist:
        return {
            'paciente_data': '',
            'paciente_json': 'null'
        }


class AtencionDetailJSONView(PermissionMixin, ListView):
    """
    Vista para obtener el detalle completo de una atención médica en formato JSON
    """
    model = Atencion
    permission_required = 'view_atencion'

    def get_object(self):
        """
        Obtiene la atención médica por ID
        """
        pk = self.kwargs.get('pk')
        return self.model.objects.get(pk=pk)

    def get(self, request, *args, **kwargs):
        try:
            print(f"🔍 AtencionDetailJSONView - Obteniendo atención con ID: {self.kwargs.get('pk')}")
            atencion = self.get_object()
            print(f"✅ Atención encontrada: {atencion.id} - Paciente: {atencion.paciente.nombres} {atencion.paciente.apellidos}")

            # Preparar datos del paciente
            from datetime import date
            edad = None
            if atencion.paciente.fecha_nacimiento:
                hoy = date.today()
                edad = hoy.year - atencion.paciente.fecha_nacimiento.year - ((hoy.month, hoy.day) < (atencion.paciente.fecha_nacimiento.month, atencion.paciente.fecha_nacimiento.day))

            paciente_data = {
                'nombre_completo': f"{atencion.paciente.nombres} {atencion.paciente.apellidos}",
                'nombres': atencion.paciente.nombres,
                'apellidos': atencion.paciente.apellidos,
                'cedula': atencion.paciente.numero_identificacion,
                'numero_identificacion': atencion.paciente.numero_identificacion,
                'email': atencion.paciente.email or '',
                'telefono': atencion.paciente.telefono or '',
                'direccion': atencion.paciente.direccion or '',
                'edad': edad,
                'fecha_nacimiento': atencion.paciente.fecha_nacimiento.isoformat() if atencion.paciente.fecha_nacimiento else None,
                'foto': atencion.paciente.foto.url if atencion.paciente.foto else None,
            }

            # Preparar datos de diagnósticos
            diagnosticos_data = []
            for diagnostico in atencion.diagnostico.all():
                diagnosticos_data.append({
                    'id': diagnostico.id,
                    'codigo': diagnostico.codigo,
                    'descripcion': diagnostico.descripcion,
                    'datos_adicionales': diagnostico.datos_adicionales or ''
                })

            # Preparar datos de medicamentos
            medicamentos_data = []
            for detalle in atencion.detalles.all():
                medicamentos_data.append({
                    'id': detalle.medicamento.id,
                    'nombre': detalle.medicamento.nombre,
                    'concentracion': detalle.medicamento.concentracion or '',
                    'tipo': detalle.medicamento.tipo.nombre if detalle.medicamento.tipo else '',
                    'marca': detalle.medicamento.marca_medicamento.nombre if detalle.medicamento.marca_medicamento else '',
                    'cantidad': detalle.cantidad,
                    'prescripcion': detalle.prescripcion,
                    'duracion': detalle.duracion_tratamiento,
                    'frecuencia_diaria': detalle.frecuencia_diaria,
                    'precio_unitario': float(detalle.precio_unitario) if detalle.precio_unitario else 0,
                    'subtotal': float(detalle.subtotal) if detalle.subtotal else 0
                })

            # Preparar respuesta completa
            data = {
                'id': atencion.id,
                'fecha_atencion': atencion.fecha_atencion.isoformat(),
                'es_control': atencion.es_control,

                # Signos vitales
                'presion_arterial': atencion.presion_arterial or '',
                'pulso': atencion.pulso if atencion.pulso is not None else '',
                'temperatura': float(atencion.temperatura) if atencion.temperatura else None,
                'frecuencia_respiratoria': atencion.frecuencia_respiratoria if atencion.frecuencia_respiratoria is not None else '',
                'saturacion_oxigeno': float(atencion.saturacion_oxigeno) if atencion.saturacion_oxigeno else None,
                'peso': float(atencion.peso) if atencion.peso else None,
                'altura': float(atencion.altura) if atencion.altura else None,

                # Evaluación clínica
                'motivo_consulta': atencion.motivo_consulta or '',
                'sintomas': atencion.sintomas or '',
                'examen_fisico': atencion.examen_fisico or '',

                # Plan terapéutico
                'tratamiento': atencion.tratamiento or '',
                'examenes_enviados': atencion.examenes_enviados or '',
                'comentario_adicional': atencion.comentario_adicional or '',

                # Datos relacionados
                'paciente': paciente_data,
                'diagnosticos': diagnosticos_data,
                'medicamentos': medicamentos_data,

                # Información del doctor
                'doctor': {
                    'nombres': atencion.doctor.nombres if atencion.doctor else '',
                    'apellidos': atencion.doctor.apellidos if atencion.doctor else '',
                    'especialidad': atencion.doctor.especialidad.nombre if atencion.doctor and atencion.doctor.especialidad else ''
                }
            }

            print(f"📊 Datos preparados - Paciente: {paciente_data['nombre_completo']}")
            print(f"📊 Diagnósticos: {len(diagnosticos_data)} encontrados")
            print(f"📊 Medicamentos: {len(medicamentos_data)} encontrados")

            return JsonResponse(data)

        except Atencion.DoesNotExist:
            print(f"❌ Atención no encontrada con ID: {self.kwargs.get('pk')}")
            return JsonResponse({
                'error': 'Atención médica no encontrada'
            }, status=404)
        except Exception as e:
            print(f"💥 Error en AtencionDetailJSONView: {str(e)}")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)