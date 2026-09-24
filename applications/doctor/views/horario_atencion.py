from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.doctor.forms.horario_atencion import HorarioAtencionForm
from applications.doctor.models import HorarioAtencion


class HorarioAtencionListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'doctor/horario_atencion/list.html'
    model = HorarioAtencion
    context_object_name = 'horarios_atencion'
    permission_required = 'view_horarioatencion'
    paginate_by = 10

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(dia_semana__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('dia_semana', 'hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('doctor:horario_atencion_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
        
        # Agregar estadísticas
        horarios = self.get_queryset()
        
        # Contar días únicos cubiertos
        dias_unicos = set(horario.dia_semana for horario in horarios)
        context['dias_cubiertos'] = len(dias_unicos)
        
        # Contar horarios con pausas
        horarios_con_pausas = horarios.filter(
            intervalo_desde__isnull=False, 
            intervalo_hasta__isnull=False
        ).count()
        context['horarios_con_pausas'] = horarios_con_pausas
        
        # Total de horarios activos
        context['horarios_activos'] = horarios.filter(activo=True).count()
            
        return context


class HorarioAtencionCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = HorarioAtencion
    template_name = 'doctor/horario_atencion/form.html'
    form_class = HorarioAtencionForm
    success_url = reverse_lazy('doctor:horario_atencion_list')
    permission_required = 'add_horarioatencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Horario de Atención'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        horario = self.object
        messages.success(self.request, f"Éxito al crear el horario de atención para {horario.get_dia_semana_display()}.")
        
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


class HorarioAtencionUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = HorarioAtencion
    template_name = 'doctor/horario_atencion/form.html'
    form_class = HorarioAtencionForm
    success_url = reverse_lazy('doctor:horario_atencion_list')
    permission_required = 'change_horarioatencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Horario de Atención'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        horario = self.object
        messages.success(self.request, f"Éxito al actualizar el horario de atención para {horario.get_dia_semana_display()}.")
        return response


class HorarioAtencionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = HorarioAtencion
    template_name = 'components/delete.html'
    success_url = reverse_lazy('doctor:horario_atencion_list')
    permission_required = 'delete_horarioatencion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Horario de Atención'
        context['description'] = f"¿Desea eliminar el horario de atención: {self.object}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        doctores_relacionados = self.object.doctores.all()
        if doctores_relacionados.exists():
            context['has_dependencies'] = True
            context['dependencies'] = doctores_relacionados
            context['dependency_message'] = f"Este horario de atención está siendo usado por {doctores_relacionados.count()} doctor(es). Debe remover este horario de los doctores antes de eliminarlo."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            horario = self.get_object()
            doctores = horario.doctores.all()
            
            # Crear mensaje detallado con los doctores afectados
            doctor_names = [f"Dr. {d.nombres} {d.apellidos}" for d in doctores[:5]]  # Limitar a 5 nombres
            doctores_text = ", ".join(doctor_names)
            if doctores.count() > 5:
                doctores_text += f" y {doctores.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar el horario de atención '{horario}' porque está asignado a los siguientes doctores: {doctores_text}. "
                f"Debe remover este horario de los doctores antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        horario_info = str(self.object)
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el horario de atención {horario_info}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            doctores = self.object.doctores.all()
            
            # Crear mensaje detallado con los doctores afectados
            doctor_names = [f"Dr. {d.nombres} {d.apellidos}" for d in doctores[:5]]  # Limitar a 5 nombres
            doctores_text = ", ".join(doctor_names)
            if doctores.count() > 5:
                doctores_text += f" y {doctores.count() - 5} más"
            
            messages.error(
                self.request, 
                f"No se puede eliminar el horario de atención '{horario_info}' porque está asignado a los siguientes doctores: {doctores_text}. "
                f"Debe remover este horario de los doctores antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)
