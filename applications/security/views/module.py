
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.security.forms.module import ModuleForm
from applications.security.models import Module
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q


class ModuleListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'security/admin/modules/list.html'
    model = Module
    context_object_name = 'modules'
    permission_required = 'view_module'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(name__icontains=q1), Q.OR)
            self.query.add(Q(menu__name__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('security:module_create')
        print(context['permissions'])
        return context


class ModuleCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Module
    template_name = 'security/admin/modules/form.html'
    form_class = ModuleForm
    success_url = reverse_lazy('security:module_list')
    permission_required = 'add_module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Módulo'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        module = self.object
        messages.success(self.request, f"Éxito al crear el módulo {module.name}.")
        
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


class ModuleUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Module
    template_name = 'security/admin/modules/form.html'
    form_class = ModuleForm
    success_url = reverse_lazy('security:module_list')
    permission_required = 'change_module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Módulo'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        module = self.object
        messages.success(self.request, f"Éxito al actualizar el módulo {module.name}.")
        return response


class ModuleDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Module
    template_name = 'components/delete.html'
    success_url = reverse_lazy('security:module_list')
    permission_required = 'delete_module'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Módulo'
        context['description'] = f"¿Desea eliminar el módulo: {self.object.name}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        group_permissions = self.object.group_permissions.all()
        if group_permissions.exists():
            context['has_dependencies'] = True
            context['dependencies'] = group_permissions
            context['dependency_message'] = f"Este módulo está siendo usado por {group_permissions.count()} grupo(s). Debe eliminar primero las asignaciones de permisos."
        else:
            context['has_dependencies'] = False
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            module = self.get_object()
            group_permissions = module.group_permissions.all()
            
            # Crear mensaje detallado con los grupos afectados
            group_names = [gp.group.name for gp in group_permissions]
            groups_text = ", ".join(group_names)
            
            messages.error(
                request, 
                f"No se puede eliminar el módulo '{module.name}' porque está asignado a los siguientes grupos: {groups_text}. "
                f"Debe eliminar primero estas asignaciones en la gestión de permisos de grupos."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        module_name = self.object.name
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el módulo {module_name}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            group_permissions = self.object.group_permissions.all()
            
            # Crear mensaje detallado con los grupos afectados
            group_names = [gp.group.name for gp in group_permissions]
            groups_text = ", ".join(group_names)
            
            messages.error(
                self.request, 
                f"No se puede eliminar el módulo '{module_name}' porque está asignado a los siguientes grupos: {groups_text}. "
                f"Debe eliminar primero estas asignaciones en la gestión de permisos de grupos."
            )
            return HttpResponseRedirect(self.success_url)