from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.security.forms.user import UserForm
from applications.security.models import User
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q


class UserListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'security/admin/users/list.html'
    model = User
    context_object_name = 'users'
    permission_required = 'view_user'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(username__icontains=q1), Q.OR)
            self.query.add(Q(first_name__icontains=q1), Q.OR)
            self.query.add(Q(last_name__icontains=q1), Q.OR)
            self.query.add(Q(email__icontains=q1), Q.OR)
            self.query.add(Q(dni__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('security:user_create')
        print(context['permissions'])
        return context


class UserCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = User
    template_name = 'security/admin/users/form.html'
    form_class = UserForm
    success_url = reverse_lazy('security:user_list')
    permission_required = 'add_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Crear Usuario'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        messages.success(self.request, f"Éxito al crear el usuario {user.get_full_name}.")
        return response


class UserUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = User
    template_name = 'security/admin/users/form.html'
    form_class = UserForm
    success_url = reverse_lazy('security:user_list')
    permission_required = 'change_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar Usuario'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        messages.success(self.request, f"Éxito al actualizar el usuario {user.get_full_name}.")
        return response


class UserDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = User
    template_name = 'components/delete.html'
    success_url = reverse_lazy('security:user_list')
    permission_required = 'delete_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Usuario'
        context['description'] = f"¿Desea eliminar el usuario: {self.object.get_full_name}?"
        context['back_url'] = self.success_url
        
        # Verificar restricciones específicas para usuarios
        has_dependencies = False
        dependency_message = ""
        dependencies = []
        
        # Verificar si es el usuario actual
        if self.object == self.request.user:
            has_dependencies = True
            dependency_message = "No puedes eliminar tu propia cuenta."
            
        # Verificar si es el último superusuario
        elif self.object.is_superuser and User.objects.filter(is_superuser=True).count() == 1:
            has_dependencies = True
            dependency_message = "No puedes eliminar el último superusuario del sistema."
        
        context['has_dependencies'] = has_dependencies
        context['dependencies'] = dependencies
        context['dependency_message'] = dependency_message
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        try:
            # Verificar si el usuario está intentando eliminarse a sí mismo
            if self.object == request.user:
                messages.error(request, "No puedes eliminar tu propia cuenta.")
                return HttpResponseRedirect(success_url)
            
            # Verificar si es el último superusuario
            if self.object.is_superuser and User.objects.filter(is_superuser=True).count() == 1:
                messages.error(request, "No puedes eliminar el último superusuario del sistema.")
                return HttpResponseRedirect(success_url)
            
            user_name = self.object.get_full_name
            self.object.delete()
            messages.success(request, f"Éxito al eliminar el usuario {user_name}.")
            
        except ProtectedError:
            messages.error(request, f"Error al eliminar el usuario {self.object.get_full_name}. Tiene registros asociados.")
        
        return HttpResponseRedirect(success_url)
