from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.tipo_medicamento import TipoMedicamentoForm
from applications.core.models import TipoMedicamento


class TipoMedicamentoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/tipo_medicamento/list.html'
    model = TipoMedicamento
    context_object_name = 'tipos_medicamento'
    permission_required = 'view_tipomedicamento'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:tipo_medicamento_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class TipoMedicamentoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = TipoMedicamento
    template_name = 'core/tipo_medicamento/form.html'
    form_class = TipoMedicamentoForm
    success_url = reverse_lazy('core:tipo_medicamento_list')
    permission_required = 'add_tipomedicamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Tipo de Medicamento'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        tipo_medicamento = self.object
        messages.success(self.request, f"Éxito al crear el tipo de medicamento {tipo_medicamento.nombre}.")
        
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


class TipoMedicamentoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = TipoMedicamento
    template_name = 'core/tipo_medicamento/form.html'
    form_class = TipoMedicamentoForm
    success_url = reverse_lazy('core:tipo_medicamento_list')
    permission_required = 'change_tipomedicamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Tipo de Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        tipo_medicamento = self.object
        messages.success(self.request, f"Éxito al actualizar el tipo de medicamento {tipo_medicamento.nombre}.")
        return response


class TipoMedicamentoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = TipoMedicamento
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:tipo_medicamento_list')
    permission_required = 'delete_tipomedicamento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Tipo de Medicamento'
        context['description'] = f"¿Desea eliminar el tipo de medicamento: {self.object.nombre}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        medicamentos = self.object.medicamentos_por_tipo.all()
        if medicamentos.exists():
            context['has_dependencies'] = True
            context['dependencies'] = medicamentos
            context['dependency_message'] = f"Este tipo de medicamento está siendo usado por {medicamentos.count()} medicamento(s). Debe cambiar el tipo de estos medicamentos antes de eliminarlo."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            tipo_medicamento = self.get_object()
            medicamentos = tipo_medicamento.medicamentos_por_tipo.all()
            
            # Crear mensaje detallado con los medicamentos afectados
            medicamento_names = [f"{m.nombre_generico}" for m in medicamentos[:5]]  # Limitar a 5 nombres
            medicamentos_text = ", ".join(medicamento_names)
            if medicamentos.count() > 5:
                medicamentos_text += f" y {medicamentos.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar el tipo de medicamento '{tipo_medicamento.nombre}' porque está asignado a los siguientes medicamentos: {medicamentos_text}. "
                f"Debe cambiar el tipo de estos medicamentos antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        tipo_medicamento_nombre = self.object.nombre
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el tipo de medicamento {tipo_medicamento_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            medicamentos = self.object.medicamentos_por_tipo.all()
            
            # Crear mensaje detallado con los medicamentos afectados
            medicamento_names = [f"{m.nombre_generico}" for m in medicamentos[:5]]  # Limitar a 5 nombres
            medicamentos_text = ", ".join(medicamento_names)
            if medicamentos.count() > 5:
                medicamentos_text += f" y {medicamentos.count() - 5} más"
            
            messages.error(
                self.request, 
                f"No se puede eliminar el tipo de medicamento '{tipo_medicamento_nombre}' porque está asignado a los siguientes medicamentos: {medicamentos_text}. "
                f"Debe cambiar el tipo de estos medicamentos antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)
