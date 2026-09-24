from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.tipo_gasto import TipoGastoForm
from applications.core.models import TipoGasto


class TipoGastoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/tipo_gasto/list.html'
    model = TipoGasto
    context_object_name = 'tipos_gasto'
    permission_required = 'view_tipogasto'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:tipo_gasto_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class TipoGastoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = TipoGasto
    template_name = 'core/tipo_gasto/form.html'
    form_class = TipoGastoForm
    success_url = reverse_lazy('core:tipo_gasto_list')
    permission_required = 'add_tipogasto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Tipo de Gasto'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        tipo_gasto = self.object
        messages.success(self.request, f"Éxito al crear el tipo de gasto {tipo_gasto.nombre}.")
        
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


class TipoGastoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = TipoGasto
    template_name = 'core/tipo_gasto/form.html'
    form_class = TipoGastoForm
    success_url = reverse_lazy('core:tipo_gasto_list')
    permission_required = 'change_tipogasto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Tipo de Gasto'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        tipo_gasto = self.object
        messages.success(self.request, f"Éxito al actualizar el tipo de gasto {tipo_gasto.nombre}.")
        return response


class TipoGastoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = TipoGasto
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:tipo_gasto_list')
    permission_required = 'delete_tipogasto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Tipo de Gasto'
        context['description'] = f"¿Desea eliminar el tipo de gasto: {self.object.nombre}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        gastos_mensuales = self.object.gastos_mensuales.all()
        if gastos_mensuales.exists():
            context['has_dependencies'] = True
            context['dependencies'] = gastos_mensuales
            context['dependency_message'] = f"Este tipo de gasto está siendo usado por {gastos_mensuales.count()} gasto(s) mensual(es). Debe cambiar el tipo de estos gastos antes de eliminarlo."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            tipo_gasto = self.get_object()
            gastos_mensuales = tipo_gasto.gastos_mensuales.all()
            
            # Crear mensaje detallado con los gastos afectados
            gasto_info = [f"{g.fecha} - ${g.valor}" for g in gastos_mensuales[:5]]  # Limitar a 5 gastos
            gastos_text = ", ".join(gasto_info)
            if gastos_mensuales.count() > 5:
                gastos_text += f" y {gastos_mensuales.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar el tipo de gasto '{tipo_gasto.nombre}' porque está asignado a los siguientes gastos mensuales: {gastos_text}. "
                f"Debe cambiar el tipo de estos gastos antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        tipo_gasto_nombre = self.object.nombre
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el tipo de gasto {tipo_gasto_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección por relaciones
            gastos_mensuales = self.object.gastos_mensuales.all()
            
            # Crear mensaje detallado con los gastos afectados
            gasto_info = [f"{g.fecha} - ${g.valor}" for g in gastos_mensuales[:5]]  # Limitar a 5 gastos
            gastos_text = ", ".join(gasto_info)
            if gastos_mensuales.count() > 5:
                gastos_text += f" y {gastos_mensuales.count() - 5} más"
            
            messages.error(
                self.request, 
                f"No se puede eliminar el tipo de gasto '{tipo_gasto_nombre}' porque está asignado a los siguientes gastos mensuales: {gastos_text}. "
                f"Debe cambiar el tipo de estos gastos antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)
