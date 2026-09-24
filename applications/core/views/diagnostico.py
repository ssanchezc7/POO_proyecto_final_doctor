from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.diagnostico import DiagnosticoForm
from applications.core.models import Diagnostico


class DiagnosticoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/diagnostico/list.html'
    model = Diagnostico
    context_object_name = 'diagnosticos'
    permission_required = 'view_diagnostico'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(codigo__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
            self.query.add(Q(datos_adicionales__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('codigo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:diagnostico_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class DiagnosticoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Diagnostico
    template_name = 'core/diagnostico/form.html'
    form_class = DiagnosticoForm
    success_url = reverse_lazy('core:diagnostico_list')
    permission_required = 'add_diagnostico'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Diagnóstico'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        diagnostico = self.object
        messages.success(self.request, f"Éxito al crear el diagnóstico {diagnostico.codigo} - {diagnostico.descripcion}.")
        
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


class DiagnosticoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Diagnostico
    template_name = 'core/diagnostico/form.html'
    form_class = DiagnosticoForm
    success_url = reverse_lazy('core:diagnostico_list')
    permission_required = 'change_diagnostico'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Diagnóstico'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        diagnostico = self.object
        messages.success(self.request, f"Éxito al actualizar el diagnóstico {diagnostico.codigo} - {diagnostico.descripcion}.")
        return response


class DiagnosticoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Diagnostico
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:diagnostico_list')
    permission_required = 'delete_diagnostico'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Diagnóstico'
        context['description'] = f"¿Desea eliminar el diagnóstico: {self.object.codigo} - {self.object.descripcion}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        atenciones = self.object.atenciones.all()
        if atenciones.exists():
            context['has_dependencies'] = True
            context['dependencies'] = atenciones
            context['dependency_message'] = f"Este diagnóstico está siendo usado en {atenciones.count()} atención(es) médica(s). No se puede eliminar porque tiene historial médico asociado."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            diagnostico = self.get_object()
            atenciones = diagnostico.atenciones.all()
            
            # Crear mensaje detallado con las atenciones afectadas
            atencion_info = [f"Atención #{a.id} - {a.paciente.nombre_completo}" for a in atenciones[:3]]  # Limitar a 3 nombres
            atenciones_text = ", ".join(atencion_info)
            if atenciones.count() > 3:
                atenciones_text += f" y {atenciones.count() - 3} más"
            
            messages.error(
                request, 
                f"No se puede eliminar el diagnóstico '{diagnostico.codigo} - {diagnostico.descripcion}' porque está registrado en las siguientes atenciones: {atenciones_text}. "
                f"Este diagnóstico forma parte del historial médico y no puede ser eliminado."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        diagnostico_info = f"{self.object.codigo} - {self.object.descripcion}"
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el diagnóstico {diagnostico_info}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            atenciones = self.object.atenciones.all()
            
            # Crear mensaje detallado con las atenciones afectadas
            atencion_info = [f"Atención #{a.id} - {a.paciente.nombre_completo}" for a in atenciones[:3]]  # Limitar a 3 nombres
            atenciones_text = ", ".join(atencion_info)
            if atenciones.count() > 3:
                atenciones_text += f" y {atenciones.count() - 3} más"
            
            messages.error(
                self.request, 
                f"No se puede eliminar el diagnóstico '{diagnostico_info}' porque está registrado en las siguientes atenciones: {atenciones_text}. "
                f"Este diagnóstico forma parte del historial médico y no puede ser eliminado."
            )
            return HttpResponseRedirect(self.success_url)
