import json
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import Group, Permission
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.security.forms.group_module_permission import GroupModulePermissionForm
from applications.security.models import Module, GroupModulePermission
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.db.models import Q


class GroupModulePermissionListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'security/admin/group_module_permissions/list.html'
    model = GroupModulePermission
    context_object_name = 'group_module_permissions'
    permission_required = 'view_groupmodulepermission'
    paginate_by = 5

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(group__name__icontains=q1), Q.OR)
            self.query.add(Q(module__name__icontains=q1), Q.OR)
        return self.model.objects.select_related('group', 'module').filter(self.query).order_by('group__name', 'module__order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('security:group_module_permission_create')
        return context


class GroupModulePermissionCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = GroupModulePermission
    template_name = 'security/admin/group_module_permissions/form.html'
    form_class = GroupModulePermissionForm
    success_url = reverse_lazy('security:group_module_permission_list')
    permission_required = 'add_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Crear Asignación de Permisos'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        gmp = self.object
        messages.success(self.request, f"Éxito al crear la asignación de permisos para {gmp.group.name} - {gmp.module.name}.")
        return response


class GroupModulePermissionUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = GroupModulePermission
    template_name = 'security/admin/group_module_permissions/form.html'
    form_class = GroupModulePermissionForm
    success_url = reverse_lazy('security:group_module_permission_list')
    permission_required = 'change_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Asignación de Permisos'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        gmp = self.object
        messages.success(self.request, f"Éxito al actualizar la asignación de permisos para {gmp.group.name} - {gmp.module.name}.")
        return response


class GroupModulePermissionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = GroupModulePermission
    template_name = 'components/delete.html'
    success_url = reverse_lazy('security:group_module_permission_list')
    permission_required = 'delete_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Asignación de Permisos'
        context['description'] = f"¿Desea eliminar la asignación de permisos del grupo '{self.object.group.name}' para el módulo '{self.object.module.name}'?"
        context['back_url'] = self.success_url
        context['has_dependencies'] = False
        return context

    def form_valid(self, form):
        gmp_info = f"{self.object.group.name} - {self.object.module.name}"
        response = super().form_valid(form)
        messages.success(self.request, f"Éxito al eliminar la asignación de permisos para {gmp_info}.")
        return response


class GetModulePermissionsView(View):
    """Vista AJAX para obtener los permisos asociados a un módulo específico"""
    # Temporalmente removemos el PermissionMixin para debugging
    # permission_required = 'view_groupmodulepermission'
    
    def get(self, request, *args, **kwargs):
        print("=== GetModulePermissionsView llamada ===")
        module_id = request.GET.get('module_id')
        print(f"module_id recibido: {module_id}")
        
        if not module_id:
            print("Error: No se proporcionó ID del módulo")
            return JsonResponse({'error': 'No se proporcionó ID del módulo'}, status=400)
        
        try:
            print(f"Buscando módulo con ID: {module_id}")
            module = Module.objects.get(id=module_id)
            print(f"Módulo encontrado: {module.name}")
            
            module_permissions = module.permissions.all()
            print(f"Permisos del módulo encontrados: {module_permissions.count()}")
            
            # Si el módulo no tiene permisos específicos, devolver lista vacía
            if not module_permissions.exists():
                print("El módulo no tiene permisos específicos")
                return JsonResponse({
                    'permissions': [],
                    'message': f'El módulo "{module.name}" no tiene permisos específicos asignados.',
                    'module_name': module.name,
                    'total_permissions': 0
                })
            
            # Formatear los permisos para enviar al frontend
            permissions_data = []
            for permission in module_permissions.order_by('content_type__model', 'name'):
                perm_data = {
                    'id': permission.id,
                    'name': permission.name,
                    'codename': permission.codename,
                    'content_type': permission.content_type.model,
                    'display_name': f"{permission.name}"
                }
                permissions_data.append(perm_data)
                print(f"Permiso procesado: {perm_data}")
            
            response_data = {
                'permissions': permissions_data,
                'module_name': module.name,
                'total_permissions': len(permissions_data)
            }
            print(f"Respuesta a enviar: {response_data}")
            return JsonResponse(response_data)
            
        except Module.DoesNotExist:
            print(f"Error: Módulo con ID {module_id} no encontrado")
            return JsonResponse({'error': 'Módulo no encontrado'}, status=404)
        except Exception as e:
            print(f"Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
