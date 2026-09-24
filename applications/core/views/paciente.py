from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.paciente import PacienteForm
from applications.core.models import Paciente

"""  Vista para buscar pacientes mediante AJAX. Por nombres, apellidos, cédula o teléfono. """


@login_required
@require_http_methods(["GET"])
def paciente_find(request):
    try:
        # Obtener el parámetro de búsqueda
        query = request.GET.get('q', '').strip()

        # Si no hay query, devolver todos los pacientes activos (limitado)
        if not query:
            pacientes_query = Paciente.objects.filter(
                activo=True
            ).select_related('tipo_sangre').order_by('apellidos', 'nombres')[:50]
        else:
            # Validar que se proporcione al menos 3 caracteres para búsqueda específica
            if len(query) < 3:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe proporcionar al menos 3 caracteres para la búsqueda',
                    'pacientes': []
                })

            # Construir la consulta de búsqueda
            # Buscar en nombres, apellidos, cédula, DNI y teléfono
            pacientes_query = Paciente.objects.filter(
                Q(activo=True) & (
                        Q(nombres__icontains=query) |
                        Q(apellidos__icontains=query) |
                        Q(cedula_ecuatoriana__icontains=query) |
                        Q(dni__icontains=query) |
                        Q(telefono__icontains=query)
                )
            ).select_related('tipo_sangre').prefetch_related(
                'atenciones__diagnostico',
                'atenciones__detalles__medicamento'
            ).order_by('apellidos', 'nombres')

            # Limitar resultados para mejorar rendimiento
            pacientes_query = pacientes_query[:20]

        # Convertir a lista de diccionarios
        pacientes_data = []
        for paciente in pacientes_query:
            # Para consultas sin query (obtener todos), solo información básica
            if not query:
                paciente_dict = {
                    'id': paciente.id,
                    'nombres': paciente.nombres,
                    'apellidos': paciente.apellidos,
                    'nombre_completo': paciente.nombre_completo,
                    'cedula_ecuatoriana': paciente.cedula_ecuatoriana,
                    'dni': paciente.dni,
                    'telefono': paciente.telefono,
                    'email': paciente.email,
                    'edad': paciente.edad,
                }
                pacientes_data.append(paciente_dict)
                continue
            
            # Para búsquedas específicas, información completa
            # Calcular edad
            edad = paciente.edad

            # Obtener atenciones anteriores (últimas 10)
            atenciones = []
            for atencion in paciente.atenciones.all()[:10]:
                # Obtener prescripciones/detalles de esta atención
                detalles = []
                for detalle in atencion.detalles.all():
                    detalle_dict = {
                        'medicamento': detalle.medicamento.nombre if detalle.medicamento else None,
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
                    'temperatura': float(atencion.temperatura) if atencion.temperatura else None,
                    'frecuencia_respiratoria': atencion.frecuencia_respiratoria,
                    'saturacion_oxigeno': float(atencion.saturacion_oxigeno) if atencion.saturacion_oxigeno else None,
                    'peso': float(atencion.peso) if atencion.peso else None,
                    'altura': float(atencion.altura) if atencion.altura else None,
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

            paciente_dict = {
                'id': paciente.id,
                'nombres': paciente.nombres,
                'apellidos': paciente.apellidos,
                'nombre_completo': paciente.nombre_completo,
                'cedula_ecuatoriana': paciente.cedula_ecuatoriana,
                'dni': paciente.dni,
                'fecha_nacimiento': paciente.fecha_nacimiento.isoformat() if paciente.fecha_nacimiento else None,
                'edad': edad,
                'telefono': paciente.telefono,
                'email': paciente.email,
                'sexo': paciente.sexo,
                'estado_civil': paciente.estado_civil,
                'direccion': paciente.direccion,
                'latitud': float(paciente.latitud) if paciente.latitud else None,
                'longitud': float(paciente.longitud) if paciente.longitud else None,
                'tipo_sangre': paciente.tipo_sangre.tipo if paciente.tipo_sangre else None,
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
            pacientes_data.append(paciente_dict)
        print(pacientes_data)
        return JsonResponse({
            'success': True,
            'pacientes': pacientes_data,
            'total': len(pacientes_data),
            'query': query
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en la búsqueda: {str(e)}',
            'pacientes': []
        }, status=500)

# === VISTAS CRUD DE PACIENTES ===

class PacienteListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/paciente/list.html'
    model = Paciente
    context_object_name = 'pacientes'
    permission_required = 'view_paciente'
    paginate_by = 10

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombres__icontains=q1), Q.OR)
            self.query.add(Q(apellidos__icontains=q1), Q.OR)
            self.query.add(Q(cedula_ecuatoriana__icontains=q1), Q.OR)
            self.query.add(Q(telefono__icontains=q1), Q.OR)
            self.query.add(Q(email__icontains=q1), Q.OR)
            self.query.add(Q(tipo_sangre__tipo__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).select_related('tipo_sangre').order_by('apellidos', 'nombres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:paciente_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class PacienteCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Paciente
    template_name = 'core/paciente/form.html'
    form_class = PacienteForm
    success_url = reverse_lazy('core:paciente_list')
    permission_required = 'add_paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Paciente'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        paciente = self.object
        messages.success(self.request, f"Éxito al crear el paciente {paciente.nombre_completo}.")
        
        # Manejar redirección después de crear
        next_url = self.request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)
        
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()


class PacienteUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Paciente
    template_name = 'core/paciente/form.html'
    form_class = PacienteForm
    success_url = reverse_lazy('core:paciente_list')
    permission_required = 'change_paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Paciente'
        context['back_url'] = self.success_url
        return context

    def get_form(self, form_class=None):
        """
        Sobrescribir para asegurar que la fecha se formatee correctamente
        """
        form = super().get_form(form_class)
        # Asegurar que la fecha de nacimiento tenga el formato correcto
        if self.object and self.object.fecha_nacimiento:
            form.initial['fecha_nacimiento'] = self.object.fecha_nacimiento.strftime('%Y-%m-%d')
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        paciente = self.object
        messages.success(self.request, f"Éxito al actualizar el paciente {paciente.nombre_completo}.")
        return response


class PacienteDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Paciente
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:paciente_list')
    permission_required = 'delete_paciente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Paciente'
        context['description'] = f"¿Desea eliminar el paciente: {self.object.nombre_completo}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        # En este caso, verificamos si el paciente tiene información crítica
        context['has_dependencies'] = False
        context['dependency_message'] = ""
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            paciente = self.get_object()
            
            messages.error(
                request, 
                f"No se puede eliminar el paciente '{paciente.nombre_completo}' porque tiene información crítica asociada. "
                f"Considere desactivar el paciente en lugar de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        paciente_nombre = self.object.nombre_completo
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el paciente {paciente_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            messages.error(
                self.request, 
                f"No se puede eliminar el paciente '{paciente_nombre}' porque tiene información crítica asociada. "
                f"Considere desactivar el paciente en lugar de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)


