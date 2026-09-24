from datetime import datetime
from django.contrib.auth.models import Group
from django.http import HttpRequest

from applications.security.models import GroupModulePermission, User



class MenuModule:
    def __init__(self, request: HttpRequest):
        self._request = request
        self._path = self._request.path
         # añade usuario, grupo y menus al diccionario data y a la session       
    def fill(self, data):
        data['user'] = self._request.user
        data['date_time'] = datetime.now()
        data['date_date'] = datetime.now().date()
        if self._request.user.is_authenticated:
            if self._request.method == 'GET':
                # añade al diccionario el listado de grupos
                data['group_list'] = self._request.user.groups.all().order_by('id')
                
                # verifica si no existe 'group_id' en la session(por defecto vacio) del request
                if 'group_id' not in self._request.session:
                    # si existe grupos se añade a la session el primer grupo con su id
                    if data['group_list'].exists():
                        self._request.session['group_id'] = data['group_list'].first().id
               
                # Verificar si hay un cambio de grupo en la URL
                group_id = self._request.GET.get('gpid', None)
                if group_id is not None:
                    try:
                        # Verificar que el grupo pertenezca al usuario
                        new_group = data['group_list'].get(id=group_id)
                        self._request.session['group_id'] = new_group.id
                    except Group.DoesNotExist:
                        # Si el grupo no existe o no pertenece al usuario, mantener el actual
                        pass

                # Establecer el grupo actual en el contexto
                if self._request.session.get('group_id'):
                    try:
                        group = Group.objects.get(id=self._request.session['group_id'])
                        # Verificar que el grupo aún pertenezca al usuario
                        if group in data['group_list']:
                            data['group'] = group
                            data['menu_list'] = self.__get_menu_list(data["user"], group)
                        else:
                            # Si el grupo ya no pertenece al usuario, resetear a uno válido
                            if data['group_list'].exists():
                                self._request.session['group_id'] = data['group_list'].first().id
                                data['group'] = data['group_list'].first()
                                data['menu_list'] = self.__get_menu_list(data["user"], data['group'])
                    except Group.DoesNotExist:
                        # Si el grupo de la sesión no existe, resetear
                        if data['group_list'].exists():
                            self._request.session['group_id'] = data['group_list'].first().id
                            data['group'] = data['group_list'].first()
                            data['menu_list'] = self.__get_menu_list(data["user"], data['group'])
                   
      
    def __get_menu_list(self, user: User, group: Group):
        # obtiene todos los modulos del grupo
        group_module_permission_list = GroupModulePermission.objects.get_group_module_permission_active_list(group.id).order_by('module__order')
      
        # obtiene la lista de menus de tal forma que no se repitan debido que un menu
        # tiene varios modulos 
        menu_unicos= group_module_permission_list.order_by('module__menu_id').distinct('module__menu_id', )
        # obtiene cada menu con sus submenus o modulos
        menu_list = [self._get_data_menu_list(x, group_module_permission_list)
            for x in menu_unicos]
        return menu_list

    def _get_data_menu_list(
            self,
            group_module_permission: GroupModulePermission,
            group_module_permission_list
    ):
        
        group_module_permissions = group_module_permission_list.filter(
            module__menu_id=group_module_permission.module.menu_id
        )
        print("Grupo: ",group_module_permission.group)
        print("menus unicos")
        print(group_module_permission.module.menu)
        print("modulos del menu")
        print(group_module_permission),
       
        return {
            'menu': group_module_permission.module.menu,
            'group_module_permission_list': group_module_permissions,
        }

