from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.medicamento import MedicamentoForm
from applications.core.models import Medicamento


class MedicamentoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/medicamento/list.html'
    model = Medicamento
    context_object_name = 'medicamentos'
    permission_required = 'view_medicamento'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
            self.query.add(Q(tipo__nombre__icontains=q1), Q.OR)
            self.query.add(Q(marca_medicamento__nombre__icontains=q1), Q.OR)
            self.query.add(Q(concentracion__icontains=q1), Q.OR)
        return self.model.objects.select_related('tipo', 'marca_medicamento').filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:medicamento_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class MedicamentoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Medicamento
    template_name = 'core/medicamento/form.html'
    form_class = MedicamentoForm
    success_url = reverse_lazy('core:medicamento_list')
    permission_required = 'add_medicamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Medicamento'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        medicamento = self.object
        messages.success(self.request, f"Éxito al crear el medicamento {medicamento.nombre}.")
        
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


class MedicamentoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Medicamento
    template_name = 'core/medicamento/form.html'
    form_class = MedicamentoForm
    success_url = reverse_lazy('core:medicamento_list')
    permission_required = 'change_medicamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        medicamento = self.object
        messages.success(self.request, f"Éxito al actualizar el medicamento {medicamento.nombre}.")
        return response


class MedicamentoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Medicamento
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:medicamento_list')
    permission_required = 'delete_medicamento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Medicamento'
        context['description'] = f"¿Desea eliminar el medicamento: {self.object.nombre}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        # Aquí podrías agregar verificaciones adicionales si el medicamento
        # está siendo usado en prescripciones, por ejemplo
        context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            medicamento = self.get_object()
            
            messages.error(
                request, 
                f"No se puede eliminar el medicamento '{medicamento.nombre}' porque está siendo usado en el sistema. "
                f"Debe desactivar las referencias a este medicamento antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        medicamento_nombre = self.object.nombre
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el medicamento {medicamento_nombre}.")
            return response
        except ProtectedError:
            # Si hay error de protección por relaciones
            messages.error(
                self.request,
                f"No se puede eliminar el medicamento '{medicamento_nombre}' porque está siendo usado en el sistema."
            )
            return HttpResponseRedirect(self.success_url)
