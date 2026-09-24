from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.security.forms.group import GroupForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q


class GroupListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'security/admin/groups/list.html'
    model = Group
    context_object_name = 'groups'
    permission_required = 'view_group'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(name__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('security:group_create')
        print(context['permissions'])
        return context


class GroupCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Group
    template_name = 'security/admin/groups/form.html'
    form_class = GroupForm
    success_url = reverse_lazy('security:group_list')
    permission_required = 'add_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Grupo'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        group = self.object
        messages.success(self.request, f"Éxito al crear el grupo {group.name}.")
        
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


class GroupUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Group
    template_name = 'security/admin/groups/form.html'
    form_class = GroupForm
    success_url = reverse_lazy('security:group_list')
    permission_required = 'change_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Grupo'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        group = self.object
        messages.success(self.request, f"Éxito al actualizar el grupo {group.name}.")
        return response


class GroupDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Group
    template_name = 'components/delete.html'
    success_url = reverse_lazy('security:group_list')
    permission_required = 'delete_group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Grupo'
        context['description'] = f"¿Desea eliminar el grupo: {self.object.name}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        module_permissions = self.object.module_permissions.all()
        users = self.object.user_set.all()
        
        has_dependencies = False
        dependencies = []
        dependency_message = ""
        
        if module_permissions.exists():
            has_dependencies = True
            dependencies.extend(module_permissions)
            dependency_message += f"Este grupo tiene {module_permissions.count()} permiso(s) de módulo asignado(s). "
            
        if users.exists():
            has_dependencies = True
            dependencies.extend(users)
            dependency_message += f"Este grupo tiene {users.count()} usuario(s) asignado(s). "
            
        if has_dependencies:
            dependency_message += "Debe eliminar primero estas asignaciones."
            
        context['has_dependencies'] = has_dependencies
        context['dependencies'] = dependencies
        context['dependency_message'] = dependency_message
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            group = self.get_object()
            module_permissions = group.module_permissions.all()
            users = group.user_set.all()
            
            # Crear mensaje detallado con las dependencias
            message_parts = []
            if module_permissions.exists():
                module_names = [mp.module.name for mp in module_permissions]
                message_parts.append(f"módulos: {', '.join(module_names)}")
                
            if users.exists():
                user_names = [user.get_full_name or user.username for user in users]
                message_parts.append(f"usuarios: {', '.join(user_names)}")
            
            dependencies_text = " y ".join(message_parts)
            
            messages.error(
                request, 
                f"No se puede eliminar el grupo '{group.name}' porque está asignado a {dependencies_text}. "
                f"Debe eliminar primero estas asignaciones."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        group_name = self.object.name
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el grupo {group_name}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            module_permissions = self.object.module_permissions.all()
            users = self.object.user_set.all()
            
            # Crear mensaje detallado con las dependencias
            message_parts = []
            if module_permissions.exists():
                module_names = [mp.module.name for mp in module_permissions]
                message_parts.append(f"módulos: {', '.join(module_names)}")
                
            if users.exists():
                user_names = [user.get_full_name or user.username for user in users]
                message_parts.append(f"usuarios: {', '.join(user_names)}")
            
            dependencies_text = " y ".join(message_parts)
            
            messages.error(
                self.request, 
                f"No se puede eliminar el grupo '{group_name}' porque está asignado a {dependencies_text}. "
                f"Debe eliminar primero estas asignaciones."
            )
            return HttpResponseRedirect(self.success_url)
