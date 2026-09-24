import os
# import django

# Configuración para ejecutar el ORM standalone
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
# django.setup()
from django.contrib.auth.models import Group, Permission
from applications.security.models import Menu, Module, User,GroupModulePermission

def pausar_y_limpiar():
    input("Presione una tecla para continuar...")
    os.system('cls' if os.name == 'nt' else 'clear')
    
# 1. Seleccionar todos los menús
def get_all_menus():
    print("ORM: Menu.objects.all()")
    return Menu.objects.all()

# 2. Seleccionar todos los módulos
def get_all_modules():
    print("ORM: Module.objects.all()")
    return Module.objects.all()

# 3. Dado un módulo, obtener el menú de ese módulo
def get_menu_of_module(module_id):
    print(f"ORM: Module.objects.select_related('menu').get(pk={module_id}).menu")
    try:
        module = Module.objects.select_related('menu').get(pk=module_id)
        return module.menu
    except Module.DoesNotExist:
        return None

# 4. Dado un menú, obtener todos los módulos de ese menú
def get_modules_of_menu(menu_id):
    print(f"ORM: Module.objects.filter(menu_id={menu_id})")
    return Module.objects.filter(menu_id=menu_id)

# 5. Seleccionar todos los usuarios
def get_all_users():
    print("\nTEMA: Listar todos los usuarios")
    print("ORM: User.objects.all()")
    print("SQL: SELECT * FROM auth_user;")
    return User.objects.all()

# 6. Seleccionar todos los grupos
def get_all_groups():
    print("\nTEMA: Listar todos los grupos")
    print("ORM: Group.objects.all()")
    print("SQL: SELECT * FROM auth_group;")
    return Group.objects.all()

# 7. Dado un usuario, obtener todos sus grupos
def get_groups_of_user(user_id):
    print(f"\nTEMA: Listar grupos de un usuario (id={user_id})")
    print(f"ORM: User.objects.get(pk={user_id}).groups.all()")
    print(f"SQL: SELECT g.* FROM auth_group g INNER JOIN auth_user_groups ug ON g.id = ug.group_id WHERE ug.user_id = {user_id};")
    try:
        user = User.objects.get(pk=user_id)
        return user.groups.all()
    except User.DoesNotExist:
        return []

# 8. Dado un grupo, obtener todos sus usuarios
def get_users_of_group(group_id):
    print(f"\nTEMA: Listar usuarios de un grupo (id={group_id})")
    print(f"ORM: Group.objects.get(pk={group_id}).user_set.all()")
    print(f"SQL: SELECT u.* FROM auth_user u INNER JOIN auth_user_groups ug ON u.id = ug.user_id WHERE ug.group_id = {group_id};")
    try:
        group = Group.objects.get(pk=group_id)
        return group.user_set.all()
    except Group.DoesNotExist:
        return []

# 9 Obtener todos los permisos del modelo Permission
def get_all_permissions():
    print("\nTEMA: Listar todos los permisos")
    print("ORM: Permission.objects.all()")
    print("SQL: SELECT * FROM auth_permission;")
    return Permission.objects.all()

# 10 Dado un usuario, obtener todos los GroupModulePermission de los grupos a los que pertenece
def get_group_module_permissions_of_user(user_id):
    print(f"\nTEMA: Listar GroupModulePermission de los grupos del usuario (id={user_id})")
    print(f"ORM: GroupModulePermission.objects.filter(group__in=User.objects.get(pk={user_id}).groups.all())")
    print(f"SQL: SELECT * FROM security_groupmodulepermission WHERE group_id IN (SELECT group_id FROM auth_user_groups WHERE user_id = {user_id});")
    try:
        user = User.objects.get(pk=user_id)
        return GroupModulePermission.objects.filter(group__in=user.groups.all())
    except User.DoesNotExist:
        return []

# 11 Dado un GroupModulePermission, obtener todos los permisos asociados
def get_permissions_of_group_module_permission(gmp_id):
    print(f"\nTEMA: Listar permisos de un GroupModulePermission (id={gmp_id})")
    print(f"ORM: GroupModulePermission.objects.get(pk={gmp_id}).permissions.all()")
    print(f"SQL: SELECT permission_id FROM security_groupmodulepermission_permissions WHERE groupmodulepermission_id = {gmp_id};")
    try:
        gmp = GroupModulePermission.objects.get(pk=gmp_id)
        return gmp.permissions.all()
    except GroupModulePermission.DoesNotExist:
        return []

# 12 Para el superusuario cuyo id=1, obtener todos los permisos, sus grupos y los módulos de GroupModulePermission
def get_all_permissions_of_superuser():
    print("\nTEMA: Listar todos los permisos del superusuario (id=1)")
    print("ORM: Permission.objects.all()")
    print("SQL: SELECT * FROM auth_permission;")
    return Permission.objects.all()

def get_superuser_groups_and_modules():
    print("\nTEMA: Listar grupos y módulos (GroupModulePermission) del superusuario (id=1)")
    print("ORM: User.objects.get(pk=1).groups.all()")
    print("ORM: GroupModulePermission.objects.filter(group__in=User.objects.get(pk=1).groups.all())")
    print("SQL: SELECT g.* FROM auth_group g INNER JOIN auth_user_groups ug ON g.id = ug.group_id WHERE ug.user_id = 1;")
    print("SQL: SELECT * FROM security_groupmodulepermission WHERE group_id IN (SELECT group_id FROM auth_user_groups WHERE user_id = 1);")
    try:
        user = User.objects.get(pk=1)
        groups = user.groups.all()
        gmp = GroupModulePermission.objects.filter(group__in=groups)
        return groups, gmp
    except User.DoesNotExist:
        return [], []

#if __name__ == "__main__":
print("SQL: SELECT * FROM security_menu;")
for menu in get_all_menus():
    print(f"- {menu.id}: {menu.name}")
pausar_y_limpiar()

print("SQL: SELECT * FROM security_module;")
for module in get_all_modules():
    print(f"- {module.id}: {module.name} (Menu: {module.menu.name})")
pausar_y_limpiar()

# Ejemplo de uso: obtener menú de un módulo
example_module_id = 1
print(f"SQL: SELECT menu_id FROM security_module WHERE id = {example_module_id};")
menu = get_menu_of_module(example_module_id)
if menu:
    print(f"\nEl módulo {example_module_id} pertenece al menú: {menu.name}")
else:
    print(f"\nNo se encontró el módulo con id {example_module_id}")
pausar_y_limpiar()

# Ejemplo de uso: obtener módulos de un menú
example_menu_id = 1
print(f"SQL: SELECT * FROM security_module WHERE menu_id = {example_menu_id};")
modules = get_modules_of_menu(example_menu_id)
print(f"\nMódulos del menú {example_menu_id}:")
for m in modules:
    print(f"- {m.name}")
pausar_y_limpiar()
# Listar todos los usuarios
users = get_all_users()
for u in users:
    print(f"- {u.id}: {u.username}")
pausar_y_limpiar()

# Listar todos los grupos
groups = get_all_groups()
for g in groups:
    print(f"- {g.id}: {g.name}")
pausar_y_limpiar()

# Listar grupos de un usuario
example_user_id = 1
user_groups = get_groups_of_user(example_user_id)
print(f"\nGrupos del usuario {example_user_id}:")
for g in user_groups:
    print(f"- {g.id}: {g.name}")
pausar_y_limpiar()

# Listar usuarios de un grupo
example_group_id = 1
group_users = get_users_of_group(example_group_id)
print(f"\nUsuarios del grupo {example_group_id}:")
for u in group_users:
    print(f"- {u.id}: {u.username}")
pausar_y_limpiar()

# Listar todos los permisos
permissions = get_all_permissions()
for p in permissions:
    print(f"- {p.id}: {p.name}")
pausar_y_limpiar()

# Dado un usuario, listar todos los GroupModulePermission de sus grupos
example_user_id = 1
gmp_list = get_group_module_permissions_of_user(example_user_id)
print(f"\nGroupModulePermission de los grupos del usuario {example_user_id}:")
for gmp in gmp_list:
    print(f"- {gmp.id}: Grupo: {gmp.group.name}, Módulo: {gmp.module.name}")
pausar_y_limpiar()

# Dado un GroupModulePermission, listar todos sus permisos
if gmp_list:
    example_gmp_id = gmp_list[0].id
    gmp_perms = get_permissions_of_group_module_permission(example_gmp_id)
    print(f"\nPermisos del GroupModulePermission {example_gmp_id}:")
    for perm in gmp_perms:
        print(f"- {perm.id}: {perm.name}")
    pausar_y_limpiar()

# Listar todos los permisos del superusuario (id=1)
superuser_perms = get_all_permissions_of_superuser()
print("\nPermisos del superusuario (id=1):")
for perm in superuser_perms:
    print(f"- {perm.id}: {perm.name}")
pausar_y_limpiar()

# Listar a qué grupos pertenece el superusuario y los módulos de GroupModulePermission
groups, gmps = get_superuser_groups_and_modules()
print("\nGrupos del superusuario (id=1):")
for g in groups:
    print(f"- {g.id}: {g.name}")
pausar_y_limpiar()

print("\nMódulos (GroupModulePermission) de los grupos del superusuario (id=1):")
for gmp in gmps:
    print(f"- Grupo: {gmp.group.name}, Módulo: {gmp.module.name}")
pausar_y_limpiar()