import json
from datetime import date, datetime, timedelta
from calendar import monthrange
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.doctor.forms.cita_medica import CitaMedicaForm, CitaMedicaCalendarioForm
from applications.doctor.models import CitaMedica, HorarioAtencion
from applications.core.models import Doctor
from applications.doctor.utils.cita_medica import EstadoCitaChoices


class CitaMedicaListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'doctor/cita_medica/list.html'
    model = CitaMedica
    context_object_name = 'citas_medicas'
    permission_required = 'view_citamedica'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        doctor_id = self.request.GET.get('doctor')
        estado = self.request.GET.get('estado')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        
        queryset = self.model.objects.select_related('paciente', 'doctor')
        
        if q1:
            self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
            self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)
            self.query.add(Q(doctor__nombres__icontains=q1), Q.OR)
            self.query.add(Q(doctor__apellidos__icontains=q1), Q.OR)
            self.query.add(Q(observaciones__icontains=q1), Q.OR)
        
        if doctor_id:
            self.query.add(Q(doctor_id=doctor_id), Q.AND)
        
        if estado:
            self.query.add(Q(estado=estado), Q.AND)
        
        if fecha_desde:
            self.query.add(Q(fecha__gte=fecha_desde), Q.AND)
        
        if fecha_hasta:
            self.query.add(Q(fecha__lte=fecha_hasta), Q.AND)
        
        return queryset.filter(self.query).order_by('fecha', 'hora_cita')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('doctor:cita_medica_create')
        context['calendario_url'] = reverse_lazy('doctor:cita_medica_calendario')
        
        # Filtros para el template
        context['doctores'] = Doctor.objects.filter(activo=True).order_by('nombres', 'apellidos')
        context['estados'] = EstadoCitaChoices.choices
        
        # Mantener filtros en el contexto
        context['filtros'] = {
            'q': self.request.GET.get('q', ''),
            'doctor': self.request.GET.get('doctor', ''),
            'estado': self.request.GET.get('estado', ''),
            'fecha_desde': self.request.GET.get('fecha_desde', ''),
            'fecha_hasta': self.request.GET.get('fecha_hasta', ''),
        }
        
        # Estadísticas rápidas
        hoy = date.today()
        context['stats'] = {
            'total': CitaMedica.objects.count(),
            'hoy': CitaMedica.objects.filter(fecha=hoy).count(),
            'esta_semana': CitaMedica.objects.filter(
                fecha__gte=hoy,
                fecha__lt=hoy + timedelta(days=7)
            ).count(),
            'pendientes': CitaMedica.objects.filter(
                estado=EstadoCitaChoices.DISPONIBLE,
                fecha__gte=hoy
            ).count(),
        }
        
        return context


class CitaMedicaCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = CitaMedica
    template_name = 'doctor/cita_medica/form.html'
    form_class = CitaMedicaForm
    success_url = reverse_lazy('doctor:cita_medica_list')
    permission_required = 'add_citamedica'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Agendar Cita Médica'
        context['back_url'] = self.success_url
        context['is_create'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cita = self.object
        messages.success(
            self.request, 
            f"Cita médica agendada exitosamente para {cita.paciente.nombre_completo} "
            f"el {cita.fecha.strftime('%d/%m/%Y')} a las {cita.hora_cita.strftime('%H:%M')}."
        )
        return response


class CitaMedicaUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = CitaMedica
    template_name = 'doctor/cita_medica/form.html'
    form_class = CitaMedicaForm
    success_url = reverse_lazy('doctor:cita_medica_list')
    permission_required = 'change_citamedica'

    def get_form_kwargs(self):
        """Asegurar que la instancia se pase correctamente al formulario"""
        kwargs = super().get_form_kwargs()
        # En las UpdateView, la instancia se establece automáticamente
        # pero vamos a asegurarnos explícitamente
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar Cita Médica'
        context['back_url'] = self.success_url
        context['is_create'] = False
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cita = self.object
        messages.success(
            self.request, 
            f"Cita médica actualizada exitosamente para {cita.paciente.nombre_completo}."
        )
        return response


class CitaMedicaDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = CitaMedica
    template_name = 'components/delete.html'
    success_url = reverse_lazy('doctor:cita_medica_list')
    permission_required = 'delete_citamedica'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Cancelar Cita Médica'
        context['description'] = (
            f"¿Desea cancelar la cita médica de {self.object.paciente.nombre_completo} "
            f"programada para el {self.object.fecha.strftime('%d/%m/%Y')} "
            f"a las {self.object.hora_cita.strftime('%H:%M')} "
            f"con el Dr. {self.object.doctor.nombre_completo}?"
        )
        context['back_url'] = self.success_url
        context['has_dependencies'] = False
        return context

    def form_valid(self, form):
        cita_info = f"{self.object.paciente.nombre_completo} - {self.object.fecha.strftime('%d/%m/%Y')} - {self.object.hora_cita.strftime('%H:%M')}"
        response = super().form_valid(form)
        messages.success(self.request, f"Cita médica cancelada exitosamente: {cita_info}")
        return response


class CitaMedicaCalendarioView(PermissionMixin, ListView):
    """Vista del calendario de citas médicas"""
    template_name = 'doctor/cita_medica/calendario.html'
    model = CitaMedica
    permission_required = 'view_citamedica'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # DEBUG: Verificar doctores disponibles
        from applications.core.models import Doctor
        doctores_todos = Doctor.objects.all()
        doctores_activos = Doctor.objects.filter(activo=True)
        print(f"=== DEBUG CALENDARIO ===")
        print(f"Total doctores en BD: {doctores_todos.count()}")
        print(f"Doctores activos: {doctores_activos.count()}")
        print("Lista de doctores activos:")
        for doctor in doctores_activos:
            print(f"  - ID: {doctor.id}, Nombre: {doctor.nombre_completo}, Activo: {doctor.activo}")
        print("=== FIN DEBUG ===")
        
        # Obtener parámetros de la URL
        doctor_id = self.request.GET.get('doctor')
        anio = int(self.request.GET.get('anio', date.today().year))
        mes = int(self.request.GET.get('mes', date.today().month))
        
        # Formulario de filtros
        initial_data = {'anio': anio, 'mes': mes}
        if doctor_id:
            initial_data['doctor'] = doctor_id
            
        form_calendario = CitaMedicaCalendarioForm(initial=initial_data)
        context['form_calendario'] = form_calendario
        
        # DEBUG: Verificar queryset del formulario
        doctor_queryset = form_calendario.fields['doctor'].queryset
        print(f"DEBUG: Queryset del formulario tiene {doctor_queryset.count()} doctores")
        
        # Información del calendario
        context['anio'] = anio
        context['mes'] = mes
        context['mes_nombre'] = date(anio, mes, 1).strftime('%B %Y')
        
        # Navegación
        fecha_anterior = date(anio, mes, 1) - timedelta(days=1)
        if mes == 12:
            fecha_siguiente = date(anio + 1, 1, 1)
        else:
            fecha_siguiente = date(anio, mes + 1, 1)
            
        context['mes_anterior'] = {
            'anio': fecha_anterior.year,
            'mes': fecha_anterior.month
        }
        context['mes_siguiente'] = {
            'anio': fecha_siguiente.year,
            'mes': fecha_siguiente.month
        }
        
        # URLs para AJAX
        context['ajax_calendario_url'] = reverse_lazy('doctor:ajax_calendario_datos')
        context['ajax_horarios_url'] = reverse_lazy('doctor:ajax_horarios_disponibles')
        context['ajax_crear_cita_url'] = reverse_lazy('doctor:ajax_crear_cita')
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class AjaxCalendarioDatosView(PermissionMixin, View):
    """Vista AJAX para obtener datos del calendario"""
    permission_required = 'view_citamedica'
    
    def get(self, request):
        doctor_id = request.GET.get('doctor')
        anio = int(request.GET.get('anio', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))
        
        if not doctor_id:
            return JsonResponse({'error': 'Doctor requerido'}, status=400)
        
        try:
            doctor = Doctor.objects.get(id=doctor_id, activo=True)
        except Doctor.DoesNotExist:
            return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
        
        # Generar calendario del mes
        calendario_data = self._generar_calendario_mes(doctor, anio, mes)
        
        return JsonResponse({
            'calendario': calendario_data,
            'doctor': doctor.nombre_completo,
            'mes': date(anio, mes, 1).strftime('%B %Y')
        })
    
    def _generar_calendario_mes(self, doctor, anio, mes):
        """Genera los datos del calendario para un mes específico"""
        dias_mes = monthrange(anio, mes)[1]
        primer_dia = date(anio, mes, 1)
        
        # Obtener todas las citas del mes
        citas = CitaMedica.objects.filter(
            doctor=doctor,
            fecha__year=anio,
            fecha__month=mes
        ).select_related('paciente')
        
        # Crear diccionario de citas por fecha
        citas_por_fecha = {}
        for cita in citas:
            fecha_str = cita.fecha.strftime('%Y-%m-%d')
            if fecha_str not in citas_por_fecha:
                citas_por_fecha[fecha_str] = []
            citas_por_fecha[fecha_str].append({
                'id': cita.id,
                'hora': cita.hora_cita.strftime('%H:%M'),
                'paciente': cita.paciente.nombre_completo,
                'estado': cita.estado,
                'observaciones': cita.observaciones or ''
            })
        
        # Obtener horarios de atención del doctor
        horarios = doctor.horarios_atencion.filter(activo=True)
        horarios_por_dia = {}
        for horario in horarios:
            horarios_por_dia[horario.dia_semana] = horario
        
        # Generar datos del calendario
        calendario = []
        for dia in range(1, dias_mes + 1):
            fecha_actual = date(anio, mes, dia)
            
            # Mapeo de días en inglés a español
            dias_semana_map = {
                'monday': 'lunes',
                'tuesday': 'martes', 
                'wednesday': 'miércoles',
                'thursday': 'jueves',
                'friday': 'viernes',
                'saturday': 'sábado',
                'sunday': 'domingo'
            }
            dia_semana_ingles = fecha_actual.strftime('%A').lower()
            dia_semana = dias_semana_map.get(dia_semana_ingles, dia_semana_ingles)
            
            fecha_str = fecha_actual.strftime('%Y-%m-%d')
            
            # Verificar si es día pasado
            es_pasado = fecha_actual < date.today()
            
            # Verificar si el doctor tiene horario este día
            tiene_horario = dia_semana in horarios_por_dia
            
            # Obtener citas del día
            citas_dia = citas_por_fecha.get(fecha_str, [])
            
            # Generar horarios disponibles si no es día pasado y tiene horario
            horarios_disponibles = []
            if not es_pasado and tiene_horario:
                horarios_disponibles = self._generar_horarios_dia(
                    doctor, horarios_por_dia[dia_semana], fecha_actual, citas_dia
                )
            
            calendario.append({
                'dia': dia,
                'fecha': fecha_str,
                'dia_semana': dia_semana,
                'es_pasado': es_pasado,
                'tiene_horario': tiene_horario,
                'citas': citas_dia,
                'horarios_disponibles': horarios_disponibles,
                'total_citas': len(citas_dia)
            })
        
        return calendario
    
    def _generar_horarios_dia(self, doctor, horario, fecha, citas_existentes):
        """Genera los horarios disponibles para un día específico"""
        horarios = []
        
        # Crear set de horas ocupadas
        horas_ocupadas = {cita['hora'] for cita in citas_existentes}
        
        # Generar horarios según la duración de cita
        duracion_cita = doctor.duracion_atencion if hasattr(doctor, 'duracion_atencion') else 30
        
        hora_actual = datetime.combine(fecha, horario.hora_inicio)
        hora_fin = datetime.combine(fecha, horario.hora_fin)
        
        while hora_actual < hora_fin:
            hora_str = hora_actual.time().strftime('%H:%M')
            
            # Verificar si está en intervalo de descanso
            en_descanso = False
            if horario.intervalo_desde and horario.intervalo_hasta:
                if horario.intervalo_desde <= hora_actual.time() < horario.intervalo_hasta:
                    en_descanso = True
            
            # Si es hoy, verificar que no sea hora pasada
            es_hora_pasada = False
            if fecha == date.today():
                es_hora_pasada = hora_actual.time() <= datetime.now().time()
            
            if not en_descanso and not es_hora_pasada:
                estado = 'ocupado' if hora_str in horas_ocupadas else 'disponible'
                horarios.append({
                    'hora': hora_str,
                    'estado': estado
                })
            
            hora_actual += timedelta(minutes=duracion_cita)
        
        return horarios


@method_decorator(csrf_exempt, name='dispatch')
class AjaxHorariosDisponiblesView(PermissionMixin, View):
    """Vista AJAX para obtener horarios disponibles de un día específico"""
    permission_required = 'view_citamedica'
    
    def get(self, request):
        doctor_id = request.GET.get('doctor')
        fecha_str = request.GET.get('fecha')
        
        if not doctor_id or not fecha_str:
            return JsonResponse({'error': 'Doctor y fecha requeridos'}, status=400)
        
        try:
            doctor = Doctor.objects.get(id=doctor_id, activo=True)
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except (Doctor.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Doctor o fecha inválidos'}, status=400)
        
        # No permitir fechas pasadas
        if fecha < date.today():
            return JsonResponse({'error': 'No se pueden agendar citas en fechas pasadas'}, status=400)
        
        # Obtener día de la semana
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

        # Verificar si el doctor tiene horario este día
        try:
            horario = doctor.horarios_atencion.get(
                dia_semana=dia_semana,
                activo=True
            )
        except HorarioAtencion.DoesNotExist:
            return JsonResponse({
                'horarios': [],
                'mensaje': f'El doctor no tiene horario de atención los {fecha.strftime("%A")}s'
            })
        
        # Obtener citas existentes para esta fecha
        citas_existentes = CitaMedica.objects.filter(
            doctor=doctor,
            fecha=fecha
        ).values_list('hora_cita', flat=True)
        
        horas_ocupadas = [hora.strftime('%H:%M') for hora in citas_existentes]
        
        # Generar horarios disponibles
        horarios_data = AjaxCalendarioDatosView()._generar_horarios_dia(
            doctor, horario, fecha, [{'hora': h} for h in horas_ocupadas]
        )
        
        return JsonResponse({
            'horarios': horarios_data,
            'doctor': doctor.nombre_completo,
            'fecha': fecha.strftime('%d/%m/%Y')
        })


@method_decorator(csrf_exempt, name='dispatch')
class AjaxCrearCitaView(PermissionMixin, View):
    """Vista AJAX para crear una cita médica"""
    permission_required = 'add_citamedica'
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            required_fields = ['doctor_id', 'paciente_id', 'fecha', 'hora']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Campo {field} requerido'}, status=400)
            
            # Obtener y validar doctor
            try:
                doctor = Doctor.objects.get(id=data['doctor_id'], activo=True)
            except Doctor.DoesNotExist:
                return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
            
            # Obtener y validar paciente
            try:
                from applications.core.models import Paciente
                paciente = Paciente.objects.get(id=data['paciente_id'], activo=True)
            except Paciente.DoesNotExist:
                return JsonResponse({'error': 'Paciente no encontrado'}, status=404)
            
            # Validar fecha y hora
            try:
                fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
                hora = datetime.strptime(data['hora'], '%H:%M').time()
            except ValueError:
                return JsonResponse({'error': 'Formato de fecha u hora inválido'}, status=400)
            
            # Crear el objeto de cita usando el formulario para validaciones
            form_data = {
                'doctor': doctor.id,
                'paciente': paciente.id,
                'fecha': fecha,
                'hora_cita': hora,
                'estado': EstadoCitaChoices.DISPONIBLE,
                'observaciones': data.get('observaciones', '')
            }
            
            form = CitaMedicaForm(data=form_data)
            
            if form.is_valid():
                cita = form.save()
                return JsonResponse({
                    'success': True,
                    'cita_id': cita.id,
                    'mensaje': f'Cita agendada exitosamente para {cita.paciente.nombre_completo}'
                })
            else:
                return JsonResponse({
                    'error': 'Datos inválidos',
                    'errores': form.errors
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
