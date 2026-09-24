from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.gasto_mensual import GastoMensualForm
from applications.core.models import GastoMensual


class GastoMensualListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/gasto_mensual/list.html'
    model = GastoMensual
    context_object_name = 'gastos_mensuales'
    permission_required = 'view_gastomensual'
    paginate_by = 10

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(tipo_gasto__nombre__icontains=q1), Q.OR)
            self.query.add(Q(observacion__icontains=q1), Q.OR)
            self.query.add(Q(valor__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).select_related('tipo_gasto').order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:gasto_mensual_create')
        
        # Calcular totales
        gastos = self.get_queryset()
        context['total_gastos'] = gastos.count()
        context['total_valor'] = sum(gasto.valor for gasto in gastos)
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class GastoMensualCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = GastoMensual
    template_name = 'core/gasto_mensual/form.html'
    form_class = GastoMensualForm
    success_url = reverse_lazy('core:gasto_mensual_list')
    permission_required = 'add_gastomensual'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Gasto Mensual'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        gasto_mensual = self.object
        messages.success(self.request, f"Éxito al crear el gasto mensual de {gasto_mensual.tipo_gasto.nombre} por ${gasto_mensual.valor}.")
        
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


class GastoMensualUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = GastoMensual
    template_name = 'core/gasto_mensual/form.html'
    form_class = GastoMensualForm
    success_url = reverse_lazy('core:gasto_mensual_list')
    permission_required = 'change_gastomensual'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Gasto Mensual'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        gasto_mensual = self.object
        messages.success(self.request, f"Éxito al actualizar el gasto mensual de {gasto_mensual.tipo_gasto.nombre} por ${gasto_mensual.valor}.")
        return response


class GastoMensualDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = GastoMensual
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:gasto_mensual_list')
    permission_required = 'delete_gastomensual'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Gasto Mensual'
        context['description'] = f"¿Desea eliminar el gasto mensual de {self.object.tipo_gasto.nombre} por ${self.object.valor} del {self.object.fecha}?"
        context['back_url'] = self.success_url
        context['has_dependencies'] = False
        return context

    def form_valid(self, form):
        # Guardar info antes de eliminar
        gasto_mensual_info = f"{self.object.tipo_gasto.nombre} por ${self.object.valor}"
        
        response = super().form_valid(form)
        messages.success(self.request, f"Éxito al eliminar el gasto mensual de {gasto_mensual_info}.")
        return response
