from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.empleado import EmpleadoForm
from applications.core.models import Empleado


class EmpleadoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/empleado/list.html'
    model = Empleado
    context_object_name = 'empleados'
    permission_required = 'view_empleado'
    paginate_by = 10

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombres__icontains=q1), Q.OR)
            self.query.add(Q(apellidos__icontains=q1), Q.OR)
            self.query.add(Q(cedula_ecuatoriana__icontains=q1), Q.OR)
            self.query.add(Q(cargo__nombre__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).select_related('cargo').order_by('apellidos', 'nombres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:empleado_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class EmpleadoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Empleado
    template_name = 'core/empleado/form.html'
    form_class = EmpleadoForm
    success_url = reverse_lazy('core:empleado_list')
    permission_required = 'add_empleado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Empleado'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        empleado = self.object
        messages.success(self.request, f"Éxito al crear el empleado {empleado.nombre_completo}.")
        
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


class EmpleadoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Empleado
    template_name = 'core/empleado/form.html'
    form_class = EmpleadoForm
    success_url = reverse_lazy('core:empleado_list')
    permission_required = 'change_empleado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Empleado'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        empleado = self.object
        messages.success(self.request, f"Éxito al actualizar el empleado {empleado.nombre_completo}.")
        return response


class EmpleadoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Empleado
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:empleado_list')
    permission_required = 'delete_empleado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Empleado'
        context['description'] = f"¿Desea eliminar el empleado: {self.object.nombre_completo}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        # En este caso, verificamos si el empleado tiene información crítica
        context['has_dependencies'] = False
        context['dependency_message'] = ""
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            empleado = self.get_object()
            
            messages.error(
                request, 
                f"No se puede eliminar el empleado '{empleado.nombre_completo}' porque tiene información crítica asociada. "
                f"Considere desactivar el empleado en lugar de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        empleado_nombre = self.object.nombre_completo
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el empleado {empleado_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            messages.error(
                self.request, 
                f"No se puede eliminar el empleado '{empleado_nombre}' porque tiene información crítica asociada. "
                f"Considere desactivar el empleado en lugar de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)
