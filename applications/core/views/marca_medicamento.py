from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.marca_medicamento import MarcaMedicamentoForm
from applications.core.models import MarcaMedicamento


class MarcaMedicamentoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/marca_medicamento/list.html'
    model = MarcaMedicamento
    context_object_name = 'marcas_medicamento'
    permission_required = 'view_marcamedicamento'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:marca_medicamento_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class MarcaMedicamentoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = MarcaMedicamento
    template_name = 'core/marca_medicamento/form.html'
    form_class = MarcaMedicamentoForm
    success_url = reverse_lazy('core:marca_medicamento_list')
    permission_required = 'add_marcamedicamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Marca de Medicamento'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        marca_medicamento = self.object
        messages.success(self.request, f"Éxito al crear la marca de medicamento {marca_medicamento.nombre}.")
        
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


class MarcaMedicamentoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = MarcaMedicamento
    template_name = 'core/marca_medicamento/form.html'
    form_class = MarcaMedicamentoForm
    success_url = reverse_lazy('core:marca_medicamento_list')
    permission_required = 'change_marcamedicamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Marca de Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        marca_medicamento = self.object
        messages.success(self.request, f"Éxito al actualizar la marca de medicamento {marca_medicamento.nombre}.")
        return response


class MarcaMedicamentoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = MarcaMedicamento
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:marca_medicamento_list')
    permission_required = 'delete_marcamedicamento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Marca de Medicamento'
        context['description'] = f"¿Desea eliminar la marca de medicamento: {self.object.nombre}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        # Aquí deberías verificar si hay medicamentos asociados a esta marca
        # Por ejemplo, si tienes un campo marca en el modelo Medicamento:
        # medicamentos = self.object.medicamentos_por_marca.all()
        # Como no veo la relación específica, lo dejo como comentario
        
        # if medicamentos.exists():
        #     context['has_dependencies'] = True
        #     context['dependencies'] = medicamentos
        #     context['dependency_message'] = f"Esta marca de medicamento está siendo usada por {medicamentos.count()} medicamento(s). Debe cambiar la marca de estos medicamentos antes de eliminarla."
        # else:
        #     context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            marca_medicamento = self.get_object()
            
            # Aquí deberías manejar las relaciones específicas
            # medicamentos = marca_medicamento.medicamentos_por_marca.all()
            
            messages.error(
                request, 
                f"No se puede eliminar la marca de medicamento '{marca_medicamento.nombre}' porque está siendo utilizada por medicamentos en el sistema. "
                f"Debe cambiar la marca de estos medicamentos antes de eliminarla."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        marca_medicamento_nombre = self.object.nombre
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar la marca de medicamento {marca_medicamento_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            messages.error(
                self.request, 
                f"No se puede eliminar la marca de medicamento '{marca_medicamento_nombre}' porque está siendo utilizada por medicamentos en el sistema. "
                f"Debe cambiar la marca de estos medicamentos antes de eliminarla."
            )
            return HttpResponseRedirect(self.success_url)
