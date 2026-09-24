from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.especialidad import EspecialidadForm
from applications.core.models import Especialidad


class EspecialidadListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/especialidad/list.html'
    model = Especialidad
    context_object_name = 'especialidades'
    permission_required = 'view_especialidad'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:especialidad_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class EspecialidadCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Especialidad
    template_name = 'core/especialidad/form.html'
    form_class = EspecialidadForm
    success_url = reverse_lazy('core:especialidad_list')
    permission_required = 'add_especialidad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Especialidad Médica'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        especialidad = self.object
        messages.success(self.request, f"Éxito al crear la especialidad médica {especialidad.nombre}.")
        
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


class EspecialidadUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Especialidad
    template_name = 'core/especialidad/form.html'
    form_class = EspecialidadForm
    success_url = reverse_lazy('core:especialidad_list')
    permission_required = 'change_especialidad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Especialidad Médica'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        especialidad = self.object
        messages.success(self.request, f"Éxito al actualizar la especialidad médica {especialidad.nombre}.")
        return response


class EspecialidadDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Especialidad
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:especialidad_list')
    permission_required = 'delete_especialidad'
    
    def post(self, request, *args, **kwargs):
        """Maneja la eliminación directa desde el modal AJAX"""
        self.object = self.get_object()
        especialidad_nombre = self.object.nombre
        
        try:
            # Verificar si tiene relaciones que impiden la eliminación
            doctores = self.object.especialidades.all()
            if doctores.exists():
                # Crear mensaje detallado con los doctores afectados
                doctor_names = [f"{d.nombres} {d.apellidos}" for d in doctores[:5]]
                doctores_text = ", ".join(doctor_names)
                if doctores.count() > 5:
                    doctores_text += f" y {doctores.count() - 5} más"
                
                messages.error(
                    request, 
                    f"No se puede eliminar la especialidad médica '{especialidad_nombre}' porque está asignada a los siguientes doctores: {doctores_text}. "
                    f"Debe cambiar la especialidad de estos doctores antes de eliminarla."
                )
            else:
                # Si no hay dependencias, proceder con la eliminación
                self.object.delete()
                messages.success(request, f"Éxito al eliminar la especialidad médica {especialidad_nombre}.")
            
            return HttpResponseRedirect(self.success_url)
            
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            doctores = self.object.especialidades.all()
            doctor_names = [f"{d.nombres} {d.apellidos}" for d in doctores[:5]]
            doctores_text = ", ".join(doctor_names)
            if doctores.count() > 5:
                doctores_text += f" y {doctores.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar la especialidad médica '{especialidad_nombre}' porque está asignada a los siguientes doctores: {doctores_text}. "
                f"Debe cambiar la especialidad de estos doctores antes de eliminarla."
            )
            return HttpResponseRedirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Especialidad Médica'
        context['description'] = f"¿Desea eliminar la especialidad médica: {self.object.nombre}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        doctores = self.object.especialidades.all()
        if doctores.exists():
            context['has_dependencies'] = True
            context['dependencies'] = doctores
            context['dependency_message'] = f"Esta especialidad médica está siendo usada por {doctores.count()} doctor(es). Debe cambiar la especialidad de estos doctores antes de eliminarla."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            especialidad = self.get_object()
            doctores = especialidad.especialidades.all()
            
            # Crear mensaje detallado con los doctores afectados
            doctor_names = [f"{d.nombres} {d.apellidos}" for d in doctores[:5]]  # Limitar a 5 nombres
            doctores_text = ", ".join(doctor_names)
            if doctores.count() > 5:
                doctores_text += f" y {doctores.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar la especialidad médica '{especialidad.nombre}' porque está asignada a los siguientes doctores: {doctores_text}. "
                f"Debe cambiar la especialidad de estos doctores antes de eliminarla."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        especialidad_nombre = self.object.nombre
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar la especialidad médica {especialidad_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            doctores = self.object.especialidades.all()
            
            # Crear mensaje detallado con los doctores afectados
            doctor_names = [f"{d.nombres} {d.apellidos}" for d in doctores[:5]]  # Limitar a 5 nombres
            doctores_text = ", ".join(doctor_names)
            if doctores.count() > 5:
                doctores_text += f" y {doctores.count() - 5} más"
            
            messages.error(
                self.request, 
                f"No se puede eliminar la especialidad médica '{especialidad_nombre}' porque está asignada a los siguientes doctores: {doctores_text}. "
                f"Debe cambiar la especialidad de estos doctores antes de eliminarla."
            )
            return HttpResponseRedirect(self.success_url)
