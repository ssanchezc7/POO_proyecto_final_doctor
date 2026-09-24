from applications.security.models import User
from django.contrib.auth.models import Group,Permission

class GroupPermission:
    @staticmethod
    # obtiene los permisos de cada modulo por grupo. Si es superusuario le asigna todos los permisos de cada modulo
    # y si no es superusuario obtiene los permisos del grupo al que pertenece   
    def get_permission_dict_of_group(user: User,group:Group):
        if user.is_superuser:
            permissions = list(Permission.objects.all().values_list('codename',flat=True))
            permissions = {x: x for x in permissions if x not in (None, '')}
        else:
            print("usuario=>",user)
            # UserGroupSession = UserGroupSession()
            # group = user.get_group_session()
            permissions = list(group.module_permissions.all().values_list('permissions__codename',flat=True))
            permissions = {x: x for x in permissions if x not in (None, '')}
        return permissions