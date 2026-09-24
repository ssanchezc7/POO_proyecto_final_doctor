import os
from django.db.models import Q

from applications.security.models import Menu, Module
# Obtener el módulo "Registro de Pacientes" por su URL
def pausar_y_limpiar():
    input("Presione una tecla para continuar...")
    os.system('cls' if os.name == 'nt' else 'clear')
    
modulo_pacientes = Module.objects.get(url='pacientes/')
print(modulo_pacientes)
pausar_y_limpiar()
# Salida: Registro de Pacientes

# Obtener el módulo "Configuración" por su nombre
modulo_config = Module.objects.get(name='Configuración')
print(f"URL: {modulo_config.url}, Menú: {modulo_config.menu.name}")
# Salida: URL: configuracion/, Menú: Administración
pausar_y_limpiar()

# Obtener un módulo por su ID (asumiendo que el ID de "Citas" es 4)
modulo_citas = Module.objects.get(id=4)
print(f"{modulo_citas.name} - {modulo_citas.description}")
# Salida: Citas - Programación de citas médicas
pausar_y_limpiar()
# Obtener todos los módulos del menú "Pacientes"
modulos_pacientes = Module.objects.filter(menu__name='Pacientes')
for m in modulos_pacientes:
    print(m.name)
pausar_y_limpiar()
# Salida:
# Registro de Pacientes
# Historial Médico
# Seguimiento

# Obtener módulos que contengan la palabra "Gestión" en su descripción
modulos_gestion = Module.objects.filter(description__icontains='gestión')
for m in modulos_gestion:
    print(f"{m.name}: {m.description}")
pausar_y_limpiar()
# Salida:
# Registro de Pacientes: Gestión de información de pacientes
# Usuarios: Gestión de usuarios del sistema

# Filtrar módulos con orden menor a 2 en cualquier menú
modulos_primeros = Module.objects.filter(order__lt=2)
for m in modulos_primeros:
    print(f"{m.name} (Menú: {m.menu.name})")
pausar_y_limpiar()
# Salida:
# Registro de Pacientes (Menú: Pacientes)
# Citas (Menú: Consultas)
# Usuarios (Menú: Administración)

# Combinar filtros: módulos del menú "Administración" con order > 1
modulos_admin_avanzados = Module.objects.filter(menu__name='Administración', order__gt=1)
for m in modulos_admin_avanzados:
    print(f"{m.name} (order: {m.order})")
pausar_y_limpiar()
# Salida:
# Configuración (order: 2)
# Reportes (order: 3)

# Usar OR lógico: módulos de "Pacientes" o "Consultas" con order=1

modulos_principales = Module.objects.filter(
    Q(menu__name='Pacientes', order=1) | Q(menu__name='Consultas', order=1)
)
for m in modulos_principales:
    print(f"{m.name} (Menú: {m.menu.name})")
pausar_y_limpiar()
# Salida:
# Registro de Pacientes (Menú: Pacientes)
# Citas (Menú: Consultas)
# Obtener el menú "Consultas"
menu_consultas = Menu.objects.get(name='Consultas')
print(f"{menu_consultas.name} (Icono: {menu_consultas.icon}, Orden: {menu_consultas.order})")
# Salida: Consultas (Icono: bi bi-calendar-check, Orden: 2)

# Obtener menús con orden mayor a 2
menus_secundarios = Menu.objects.filter(order__gt=2)
for m in menus_secundarios:
    print(f"{m.name} (order: {m.order})")
# Salida:
# Administración (order: 4)

# Obtener menús ordenados por orden ascendente
menus_ordenados = Menu.objects.all().order_by('order')
for m in menus_ordenados:
    print(f"{m.name} (order: {m.order})")
# Salida:
# Pacientes (order: 1)
# Consultas (order: 2)
# Administración (order: 4)

# Seleccionar el menú "Administración" y obtener todos sus módulos
menu_admin = Menu.objects.get(name='Administración')
modulos_admin = menu_admin.modules.all()
print(f"Módulos del menú {menu_admin.name}:")
for m in modulos_admin:
    print(f"- {m.name} (url: {m.url})")
# Salida:
# Módulos del menú Administración:
# - Usuarios (url: usuarios/)
# - Configuración (url: configuracion/)
# - Reportes (url: reportes/)

# Obtener y ordenar módulos del menú "Pacientes" por nombre
menu_pacientes = Menu.objects.get(name='Pacientes')
modulos_pacientes_por_nombre = menu_pacientes.modules.all().order_by('name')
print(f"Módulos de {menu_pacientes.name} ordenados por nombre:")
for m in modulos_pacientes_por_nombre:
    print(f"- {m.name}")
# Salida:
# Módulos de Pacientes ordenados por nombre:
# - Historial Médico
# - Registro de Pacientes
# - Seguimiento

# Obtener el módulo "Recetas" con su menú relacionado
modulo_recetas = Module.objects.select_related('menu').get(name='Recetas')
print(f"Módulo: {modulo_recetas.name}")
print(f"Pertenece al menú: {modulo_recetas.menu.name}")
print(f"Descripción: {modulo_recetas.description}")
# Salida:
# Módulo: Recetas
# Pertenece al menú: Consultas
# Descripción: Emisión de recetas médicas

# Obtener módulos del menú "Consultas" ordenados por orden
menu_consultas = Menu.objects.get(name='Consultas')
modulos_consultas = menu_consultas.modules.all().order_by('order')
print(f"Módulos de {menu_consultas.name} en orden:")
for i, m in enumerate(modulos_consultas, 1):
    print(f"{i}. {m.name} (order: {m.order})")
# Salida:
# Módulos de Consultas en orden:
# 1. Citas (order: 1)
# 2. Diagnósticos (order: 2)
# 3. Recetas (order: 3)
# Obtener conteo de módulos por menú
from django.db.models import Count
conteo_por_menu = Menu.objects.annotate(total_modules=Count('modules')).values('name', 'total_modules')
print("Cantidad de módulos por menú:")
for item in conteo_por_menu:
    print(f"- {item['name']}: {item['total_modules']} módulos")
x=input("Presione una tecla para continuar...")
# Salida:
# Cantidad de módulos por menú:
# - Pacientes: 3 módulos
# - Consultas: 3 módulos
# - Administración: 3 módulos

# Menús con sus módulos (usando prefetch_related para optimizar)
menus_con_modulos = Menu.objects.prefetch_related('modules').all().order_by('order')
for menu in menus_con_modulos:
    print(f"\nMenú: {menu.name}")
    print("Módulos:")
    for modulo in menu.modules.all().order_by('order'):
        print(f"- {modulo.name} (url: {modulo.url})")
# Salida:
# Menú: Pacientes
# Módulos:
# - Registro de Pacientes (url: pacientes/)
# - Historial Médico (url: historial/)
# - Seguimiento (url: seguimiento/)
#
# Menú: Consultas
# Módulos:
# - Citas (url: citas/)
# - Diagnósticos (url: diagnosticos/)
# - Recetas (url: recetas/)
#
# Menú: Administración
# Módulos:
# - Usuarios (url: usuarios/)
# - Configuración (url: configuracion/)
# - Reportes (url: reportes/)

# Buscar módulos que contengan "médic" en nombre o descripción

modulos_medicos = Module.objects.filter(
    Q(name__icontains='médic') | Q(description__icontains='médic')
)
print("Módulos relacionados con medicina:")
for m in modulos_medicos:
    print(f"- {m.name}: {m.description}")
# Salida:
# Módulos relacionados con medicina:
# - Historial Médico: Historial clínico de pacientes
# - Citas: Programación de citas médicas
# - Diagnósticos: Registro de diagnósticos médicos
# - Recetas: Emisión de recetas médicas