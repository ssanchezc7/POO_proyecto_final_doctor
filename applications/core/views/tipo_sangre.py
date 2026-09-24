from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.tipo_sangre import TipoSangreForm
from applications.core.models import TipoSangre


class TipoSangreListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/tipo_sangre/list.html'
    model = TipoSangre
    context_object_name = 'tipos_sangre'
    permission_required = 'view_tiposangre'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(tipo__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('tipo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:tipo_sangre_create')
        return context


class TipoSangreCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = TipoSangre
    template_name = 'core/tipo_sangre/form.html'
    form_class = TipoSangreForm
    success_url = reverse_lazy('core:tipo_sangre_list')
    permission_required = 'add_tiposangre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Tipo de Sangre'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        tipo_sangre = self.object
        messages.success(self.request, f"Éxito al crear el tipo de sangre {tipo_sangre.tipo}.")
        
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


class TipoSangreUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = TipoSangre
    template_name = 'core/tipo_sangre/form.html'
    form_class = TipoSangreForm
    success_url = reverse_lazy('core:tipo_sangre_list')
    permission_required = 'change_tiposangre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Tipo de Sangre'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        tipo_sangre = self.object
        messages.success(self.request, f"Éxito al actualizar el tipo de sangre {tipo_sangre.tipo}.")
        return response


class TipoSangreDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = TipoSangre
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:tipo_sangre_list')
    permission_required = 'delete_tiposangre'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Tipo de Sangre'
        context['description'] = f"¿Desea eliminar el tipo de sangre: {self.object.tipo}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        pacientes = self.object.tipos_sangre.all()
        if pacientes.exists():
            context['has_dependencies'] = True
            context['dependencies'] = pacientes
            context['dependency_message'] = f"Este tipo de sangre está siendo usado por {pacientes.count()} paciente(s). Debe cambiar el tipo de sangre de estos pacientes antes de eliminarlo."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            tipo_sangre = self.get_object()
            pacientes = tipo_sangre.tipos_sangre.all()
            
            # Crear mensaje detallado con los pacientes afectados
            paciente_names = [f"{p.nombres} {p.apellidos}" for p in pacientes[:5]]  # Limitar a 5 nombres
            pacientes_text = ", ".join(paciente_names)
            if pacientes.count() > 5:
                pacientes_text += f" y {pacientes.count() - 5} más"
            
            messages.error(
                request, 
                f"No se puede eliminar el tipo de sangre '{tipo_sangre.tipo}' porque está asignado a los siguientes pacientes: {pacientes_text}. "
                f"Debe cambiar el tipo de sangre de estos pacientes antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        tipo_sangre_tipo = self.object.tipo
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el tipo de sangre {tipo_sangre_tipo}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            pacientes = self.object.tipos_sangre.all()
            
            # Crear mensaje detallado con los pacientes afectados
            paciente_names = [f"{p.nombres} {p.apellidos}" for p in pacientes[:5]]  # Limitar a 5 nombres
            pacientes_text = ", ".join(paciente_names)
            if pacientes.count() > 5:
                pacientes_text += f" y {pacientes.count() - 5} más"
            
            messages.error(
                self.request, 
                f"No se puede eliminar el tipo de sangre '{tipo_sangre_tipo}' porque está asignado a los siguientes pacientes: {pacientes_text}. "
                f"Debe cambiar el tipo de sangre de estos pacientes antes de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)
