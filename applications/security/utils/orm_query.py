import os
from applications.security.models import Menu
from django.db.models import Q, Count, Max, Min, Avg

def pausar_y_limpiar():
    input("Presione una tecla para continuar...")
    os.system('cls' if os.name == 'nt' else 'clear')

# Consulta 1: Obtener todos los menús: devuelve un queryset: lista de objetos Menu
print("Sentencia: Menu.objects.all()")
todos_los_menus = Menu.objects.all().order_by('id')
print("Resultado:", todos_los_menus)
pausar_y_limpiar()

# Consulta 2: Usando filter sin condiciones
print("Sentencia: Menu.objects.filter()")
todos_los_menus = Menu.objects.filter()
print("Resultado:", todos_los_menus)
pausar_y_limpiar()

# Consulta 3: Usando values para obtener diccionarios
print("Sentencia: Menu.objects.values('id', 'name', 'icon', 'order')")
menus_valores = Menu.objects.values('id', 'name', 'icon', 'order')
print("Resultado (QuerySet):", menus_valores)
menus_valores_lista = list(menus_valores)
print("Resultado como lista de diccionarios:", menus_valores_lista)
pausar_y_limpiar()

#Consulta 4: Usando values_list para obtener tuplas
print("Sentencia: Menu.objects.values_list('id', 'name', 'icon', 'order')")
menus_valores_tuplas = Menu.objects.values_list('id', 'name', 'icon', 'order')
print("Resultado (QuerySet):", menus_valores_tuplas)
menus_valores_tuplas_lista = list(menus_valores_tuplas)
print("Resultado como lista de tuplas:", menus_valores_tuplas_lista)
pausar_y_limpiar()

# Consulta 5: Usando values_list con flat=True
print("Sentencia: Menu.objects.values_list('name', flat=True)")
nombres_menus = Menu.objects.values_list('name', flat=True)
print("Resultado (QuerySet):", nombres_menus)
nombres_menus_lista = list(nombres_menus)
print("Resultado como lista de nombres:", nombres_menus_lista)
pausar_y_limpiar()

# Consulta 6: Convertir QuerySet a lista
print("Sentencia: list(Menu.objects.all())")
menus_lista = list(Menu.objects.all())
print("Resultado:", menus_lista)
pausar_y_limpiar()

print("Sentencia: Recorrido de list(Menu.objects.all())")
print(""" for menu in menus_lista:  print(menu.id, menu.name)""")
# recorrido de la lista
for menu in menus_lista:
    print(menu.id, menu.name)
pausar_y_limpiar()

# Consulta 7: Obtener menú por ID
print("Sentencia: Menu.objects.get(id=1)")
menu = Menu.objects.get(id=1)
print("Resultado:", menu)
pausar_y_limpiar()

# Consulta 8: Obtener menú por nombre
print("Sentencia: Menu.objects.get(name='Admin')")
menu = Menu.objects.get(name='Consultas')
print("Resultado:", menu)
pausar_y_limpiar()

# Consulta 9: Filtrar por icono
print("Sentencia: Menu.objects.filter(icon='bi bi-calendar-x-fill')")
menus_filtrados = Menu.objects.filter(icon='bi bi-calendar-x-fill')
print("Resultado:", menus_filtrados)
pausar_y_limpiar()

# Consulta 10: Excluir por icono
print("Sentencia: Menu.objects.exclude(icon='bi bi-calendar-x-fill')")
menus_excluidos = Menu.objects.exclude(icon='bi bi-calendar-x-fill')
print("Resultado:", menus_excluidos)
pausar_y_limpiar()

# Consulta 11: Obtener primer menú
print("Sentencia: Menu.objects.first()")
primer_menu = Menu.objects.first()
print("Resultado:", primer_menu)
pausar_y_limpiar()

# Consulta 12: Obtener último menú
print("Sentencia: Menu.objects.last()")
ultimo_menu = Menu.objects.last()
print("Resultado:", ultimo_menu)
pausar_y_limpiar()

# Consulta 13: Verificar si existen menús
print("Sentencia: Menu.objects.exists()")
tiene_menus = Menu.objects.exists()
print("Resultado:", tiene_menus)
pausar_y_limpiar()

# Consulta 14: Ordenar por campo
print("Sentencia: Menu.objects.order_by('order')")
menus_ordenados = Menu.objects.order_by('order')
print("Resultado:", menus_ordenados)
pausar_y_limpiar()

# Consulta 15: Ordenar descendente
print("Sentencia: Menu.objects.order_by('-order')")
menus_ordenados_desc = Menu.objects.order_by('-order')
print("Resultado:", menus_ordenados_desc)
pausar_y_limpiar()

# Consulta 16: Ordenar por múltiples campos
print("Sentencia: Menu.objects.order_by('order', 'name')")
menus_orden_multiple = Menu.objects.order_by('order', 'name')
print("Resultado:", menus_orden_multiple)
pausar_y_limpiar()

# Consulta 17: Búsqueda que contiene (case sensitive)
print("Sentencia: Menu.objects.filter(name__contains='admin')")
menus_contiene = Menu.objects.filter(name__icontains='admin')
print("Resultado:", menus_contiene)
pausar_y_limpiar()

# Consulta 18: Búsqueda que contiene (case insensitive)
print("Sentencia: Menu.objects.filter(name__icontains='admin')")
menus_icontiene = Menu.objects.filter(name__icontains='admin')
print("Resultado:", menus_icontiene)
pausar_y_limpiar()

# Consulta 19: Comienza con
print("Sentencia: Menu.objects.filter(name__startswith='A')")
menus_comienza = Menu.objects.filter(name__startswith='A')
print("Resultado:", menus_comienza)
pausar_y_limpiar()

# Consulta 20: Termina con
print("Sentencia: Menu.objects.filter(name__endswith='n')")
menus_termina = Menu.objects.filter(name__endswith='n')
print("Resultado:", menus_termina)
pausar_y_limpiar()

# Consulta 21: Mayor que
print("Sentencia: Menu.objects.filter(order__gt=5)")
menus_mayor = Menu.objects.filter(order__gt=5)
print("Resultado:", menus_mayor)
pausar_y_limpiar()

# Consulta 22: Menor que
print("Sentencia: Menu.objects.filter(order__lt=5)")
menus_menor = Menu.objects.filter(order__lt=5)
print("Resultado:", menus_menor)
pausar_y_limpiar()

# Consulta 23: En una lista
print("Sentencia: Menu.objects.filter(name__in=['Admin', 'Usuario', 'Reportes'])")
menus_en_lista = Menu.objects.filter(name__in=['Admin', 'Usuario', 'Reportes'])
print("Resultado:", menus_en_lista)
pausar_y_limpiar()

# Consulta 24: En un rango
print("Sentencia: Menu.objects.filter(order__range=(1, 5))")
menus_rango = Menu.objects.filter(order__range=(1, 5))
print("Resultado:", menus_rango)
pausar_y_limpiar()

# Consulta 25: Condición OR
print("Sentencia: Menu.objects.filter(Q(name='Admin') | Q(name='Usuario'))")
menus_or = Menu.objects.filter(Q(name='Admin') | Q(name='Usuario'))
print("Resultado:", menus_or)
pausar_y_limpiar()

# Consulta 26: Condición AND
print("Sentencia: Menu.objects.filter(Q(name='Admin') & Q(order__gt=5))")
menus_and = Menu.objects.filter(Q(name='Admin') & Q(order__gt=5))
print("Resultado:", menus_and)
pausar_y_limpiar()

# Consulta 27: Condición NOT
print("Sentencia: Menu.objects.filter(~Q(name='Admin'))")
menus_not = Menu.objects.filter(~Q(name='Admin'))
print("Resultado:", menus_not)
pausar_y_limpiar()

# Consulta 28: Contar
print("Sentencia: Menu.objects.count()")
cantidad_menus = Menu.objects.count()
print("Resultado:", cantidad_menus)
pausar_y_limpiar()

# Consulta 29: Valor máximo
print("Sentencia: Menu.objects.aggregate(Max('order'))")
orden_maximo = Menu.objects.aggregate(Max('order'))
print("Resultado:", orden_maximo)
pausar_y_limpiar()

# Consulta 30: Valor mínimo
print("Sentencia: Menu.objects.aggregate(Min('order'))")
orden_minimo = Menu.objects.aggregate(Min('order'))
print("Resultado:", orden_minimo)
pausar_y_limpiar()

# Consulta 31: Promedio
print("Sentencia: Menu.objects.aggregate(Avg('order'))")
orden_promedio = Menu.objects.aggregate(Avg('order'))
print("Resultado:", orden_promedio)
pausar_y_limpiar()

# Consulta 32: Primeros 5 menús
print("Sentencia: Menu.objects.all()[:5]")
menus_limitados = Menu.objects.all()[:5]
print("Resultado:", menus_limitados)
pausar_y_limpiar()

# Consulta 33: Menús del 5 al 10
print("Sentencia: Menu.objects.all()[5:10]")
menus_segmento = Menu.objects.all()[5:10]
print("Resultado:", menus_segmento)
pausar_y_limpiar()
""" Module.objects.filter( Q(url__icontains="security") & Q(id__lt=9) )
Out[42]: SELECT "security_module"."id",
       "security_module"."url",
       "security_module"."name",
       "security_module"."menu_id",
       "security_module"."description",
       "security_module"."icon",
       "security_module"."is_active",
       "security_module"."order"
  FROM "security_module"
 INNER JOIN "security_menu"
    ON ("security_module"."menu_id" = "security_menu"."id")
 WHERE (UPPER("security_module"."url"::text) LIKE UPPER('%security%') AND "security_module"."id" < 9)     
 ORDER BY "security_menu"."order" ASC,
          "security_menu"."name" ASC,
          "security_module"."order" ASC,
          "security_module"."name" ASC
 LIMIT 21 """