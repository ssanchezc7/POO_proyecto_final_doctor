from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.cargo import CargoForm
from applications.core.models import Cargo


class CargoListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/cargo/list.html'
    model = Cargo
    context_object_name = 'cargos'
    permission_required = 'view_cargo'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:cargo_create')
        return context


class CargoCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Cargo
    template_name = 'core/cargo/form.html'
    form_class = CargoForm
    success_url = reverse_lazy('core:cargo_list')
    permission_required = 'add_cargo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Cargo'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cargo = self.object
        messages.success(self.request, f"Éxito al crear el cargo {cargo.nombre}.")
        
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


class CargoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Cargo
    template_name = 'core/cargo/form.html'
    form_class = CargoForm
    success_url = reverse_lazy('core:cargo_list')
    permission_required = 'change_cargo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Cargo'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cargo = self.object
        messages.success(self.request, f"Éxito al actualizar el cargo {cargo.nombre}.")
        return response


class CargoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Cargo
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:cargo_list')
    permission_required = 'delete_cargo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Cargo'
        context['description'] = f"¿Desea eliminar el cargo: {self.object.nombre}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        # Ajustar según las relaciones que tenga el modelo Cargo
        try:
            # Si hay empleados asociados (usando related_name="cargos")
            if hasattr(self.object, 'cargos'):
                empleados = self.object.cargos.all()
                if empleados.exists():
                    context['has_dependencies'] = True
                    context['dependencies'] = empleados
                    context['dependency_message'] = f"Este cargo está siendo usado por {empleados.count()} empleado(s). Debe cambiar el cargo de estos empleados antes de eliminarlo."
                else:
                    context['has_dependencies'] = False
            else:
                context['has_dependencies'] = False
        except:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            cargo = self.get_object()
            
            try:
                if hasattr(cargo, 'cargos'):
                    empleados = cargo.cargos.all()
                    
                    # Crear mensaje detallado con los empleados afectados
                    empleado_names = [f"{e.nombres} {e.apellidos}" for e in empleados[:5]]  # Limitar a 5 nombres
                    empleados_text = ", ".join(empleado_names)
                    if empleados.count() > 5:
                        empleados_text += f" y {empleados.count() - 5} más"
                    
                    messages.error(
                        request, 
                        f"No se puede eliminar el cargo '{cargo.nombre}' porque está asignado a los siguientes empleados: {empleados_text}. "
                        f"Debe cambiar el cargo de estos empleados antes de eliminarlo."
                    )
                else:
                    messages.error(
                        request, 
                        f"No se puede eliminar el cargo '{cargo.nombre}' porque está siendo utilizado en el sistema."
                    )
            except:
                messages.error(
                    request, 
                    f"No se puede eliminar el cargo '{cargo.nombre}' porque está siendo utilizado en el sistema."
                )
            
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        cargo_nombre = self.object.nombre
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el cargo {cargo_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            try:
                if hasattr(self.object, 'cargos'):
                    empleados = self.object.cargos.all()
                    
                    # Crear mensaje detallado con los empleados afectados
                    empleado_names = [f"{e.nombres} {e.apellidos}" for e in empleados[:5]]  # Limitar a 5 nombres
                    empleados_text = ", ".join(empleado_names)
                    if empleados.count() > 5:
                        empleados_text += f" y {empleados.count() - 5} más"
                    
                    messages.error(
                        self.request, 
                        f"No se puede eliminar el cargo '{cargo_nombre}' porque está asignado a los siguientes empleados: {empleados_text}. "
                        f"Debe cambiar el cargo de estos empleados antes de eliminarlo."
                    )
                else:
                    messages.error(
                        self.request, 
                        f"No se puede eliminar el cargo '{cargo_nombre}' porque está siendo utilizado en el sistema."
                    )
            except:
                messages.error(
                    self.request, 
                    f"No se puede eliminar el cargo '{cargo_nombre}' porque está siendo utilizado en el sistema."
                )
            
            return HttpResponseRedirect(self.success_url)
