from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.doctor.forms.servicios_adicionales import ServiciosAdicionalesForm
from applications.doctor.models import ServiciosAdicionales


class ServiciosAdicionalesListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'doctor/servicios_adicionales/list.html'
    model = ServiciosAdicionales
    context_object_name = 'servicios_adicionales'
    permission_required = 'view_serviciosadicionales'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre_servicio__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre_servicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('doctor:servicios_adicionales_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class ServiciosAdicionalesCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = ServiciosAdicionales
    template_name = 'doctor/servicios_adicionales/form.html'
    form_class = ServiciosAdicionalesForm
    success_url = reverse_lazy('doctor:servicios_adicionales_list')
    permission_required = 'add_serviciosadicionales'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Servicio Adicional'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        servicio_adicional = self.object
        messages.success(self.request, f"Éxito al crear el servicio adicional {servicio_adicional.nombre_servicio}.")
        
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


class ServiciosAdicionalesUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = ServiciosAdicionales
    template_name = 'doctor/servicios_adicionales/form.html'
    form_class = ServiciosAdicionalesForm
    success_url = reverse_lazy('doctor:servicios_adicionales_list')
    permission_required = 'change_serviciosadicionales'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Servicio Adicional'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        servicio_adicional = self.object
        messages.success(self.request, f"Éxito al actualizar el servicio adicional {servicio_adicional.nombre_servicio}.")
        return response


class ServiciosAdicionalesDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = ServiciosAdicionales
    template_name = 'components/delete.html'
    success_url = reverse_lazy('doctor:servicios_adicionales_list')
    permission_required = 'delete_serviciosadicionales'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Servicio Adicional'
        context['description'] = f"¿Desea eliminar el servicio adicional: {self.object.nombre_servicio}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        # Verificar si hay detalles de pago asociados a este servicio
        detalles_pago = self.object.detalles_pago.all()
        if detalles_pago.exists():
            context['has_dependencies'] = True
            context['dependencies'] = detalles_pago
            context['dependency_message'] = f"Este servicio adicional está siendo usado por {detalles_pago.count()} pago(s). Debe cambiar o eliminar estos pagos antes de eliminarlo."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            servicio_adicional = self.get_object()
            detalles_pago = servicio_adicional.detalles_pago.all()
            
            # Crear mensaje detallado con los pagos afectados
            pago_names = [f"Pago #{d.pago.id}" for d in detalles_pago[:5]]  # Limitar a 5 nombres
            pagos_text = ", ".join(pago_names)
            if detalles_pago.count() > 5:
                pagos_text += f" y {detalles_pago.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar el servicio adicional '{servicio_adicional.nombre_servicio}' porque está asignado a los siguientes pagos: {pagos_text}. "
                f"Debe cambiar o eliminar estos registros antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f"Éxito al eliminar el servicio adicional.")
            return response
        except Exception as e:
            messages.error(self.request, f"Error al eliminar el servicio adicional: {str(e)}")
            return HttpResponseRedirect(self.success_url)
