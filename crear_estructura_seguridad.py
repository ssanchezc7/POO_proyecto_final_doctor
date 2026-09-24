#!/usr/bin/env python
"""
Script para crear/replicar toda la estructura de menús, módulos, grupos y permisos
del sistema de seguridad.

Este script puede ejecutarse para:
1. Recrear toda la estructura desde cero
2. Actualizar datos existentes
3. Verificar la integridad de la estructura

Autor: Sistema de Seguridad
Fecha: Enero 2025
"""
import os
import django

# Configuración para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from applications.security.models import Menu, Module, GroupModulePermission, User
from django.db import transaction


class SecurityDataSeeder:
    """Clase para crear/actualizar toda la estructura de seguridad"""
    
    def __init__(self):
        self.created_count = {
            'menus': 0,
            'modules': 0,
            'groups': 0,
            'group_module_permissions': 0
        }
        self.updated_count = {
            'menus': 0,
            'modules': 0,
            'groups': 0,
            'group_module_permissions': 0
        }
    
    def create_menus(self):
        """Crear todos los menús del sistema"""
        print("📋 Creando/actualizando menús...")
        
        menus_data = [
            {
                'name': 'GASTOS Y FACTURACION',
                'icon': 'fa-solid fa-money-check-dollar',
                'order': 0
            },
            {
                'name': 'ADMINISTRACIÓN DEL SISTEMA',
                'icon': 'fas fa-cogs',
                'order': 1
            },
            {
                'name': 'GESTIÓN CLÍNICA',
                'icon': 'fas fa-hospital',
                'order': 2
            },
            {
                'name': 'FARMACIA Y MEDICAMENTOS',
                'icon': 'fas fa-pills',
                'order': 3
            },
            {
                'name': 'LABORATORIO CLÍNICO',
                'icon': 'fas fa-microscope',
                'order': 4
            },
            {
                'name': 'RECURSOS HUMANOS',
                'icon': 'fas fa-users',
                'order': 5
            }
        ]
        
        for menu_data in menus_data:
            menu, created = Menu.objects.get_or_create(
                name=menu_data['name'],
                defaults={
                    'icon': menu_data['icon'],
                    'order': menu_data['order']
                }
            )
            if created:
                self.created_count['menus'] += 1
                print(f"  ✅ Creado: {menu.name}")
            else:
                # Actualizar si es necesario
                updated = False
                if menu.icon != menu_data['icon']:
                    menu.icon = menu_data['icon']
                    updated = True
                if menu.order != menu_data['order']:
                    menu.order = menu_data['order']
                    updated = True
                if updated:
                    menu.save()
                    self.updated_count['menus'] += 1
                    print(f"  🔄 Actualizado: {menu.name}")
                else:
                    print(f"  ✓ Ya existe: {menu.name}")
    
    def create_modules(self):
        """Crear todos los módulos del sistema"""
        print("\n📁 Creando/actualizando módulos...")
        
        modules_data = [
            # GASTOS Y FACTURACION
            {
                'name': 'PAGOS',
                'url': '/doctor/pagos/dashboard/',
                'menu_name': 'GASTOS Y FACTURACION',
                'description': 'Gestión de pagos médicos',
                'icon': 'fas fa-credit-card',
                'order': 1
            },
            {
                'name': 'TIPO DE GASTO',
                'url': '/core/tipo_gasto_list/',
                'menu_name': 'GASTOS Y FACTURACION',
                'description': 'Catálogo de tipos de gastos',
                'icon': 'fas fa-tags',
                'order': 2
            },
            {
                'name': 'GASTOS MENSUALES',
                'url': '/core/gasto_mensual_list/',
                'menu_name': 'GASTOS Y FACTURACION',
                'description': 'Registro de gastos mensuales',
                'icon': 'fas fa-calendar-alt',
                'order': 3
            },
            
            # ADMINISTRACIÓN DEL SISTEMA
            {
                'name': 'USUARIOS',
                'url': '/auth/user_list/',
                'menu_name': 'ADMINISTRACIÓN DEL SISTEMA',
                'description': 'Gestión de usuarios del sistema',
                'icon': 'fas fa-users',
                'order': 1
            },
            {
                'name': 'MODULOS',
                'url': '/auth/module_list/',
                'menu_name': 'ADMINISTRACIÓN DEL SISTEMA',
                'description': 'Gestión de módulos del sistema',
                'icon': 'fas fa-cube',
                'order': 2
            },
            {
                'name': 'MENUS',
                'url': '/auth/menu_list/',
                'menu_name': 'ADMINISTRACIÓN DEL SISTEMA',
                'description': 'Gestión de menús del sistema',
                'icon': 'fas fa-list',
                'order': 3
            },
            {
                'name': 'GRUPOS MODULOS',
                'url': '/auth/group_module_permission_list/',
                'menu_name': 'ADMINISTRACIÓN DEL SISTEMA',
                'description': 'Asignación de permisos grupo-módulo',
                'icon': 'fas fa-shield-alt',
                'order': 4
            },
            {
                'name': 'GRUPOS',
                'url': '/auth/group_list/',
                'menu_name': 'ADMINISTRACIÓN DEL SISTEMA',
                'description': 'Gestión de grupos de usuarios',
                'icon': 'fas fa-users-cog',
                'order': 5
            },
            
            # GESTIÓN CLÍNICA
            {
                'name': 'PACIENTES',
                'url': '/core/paciente_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Registro y gestión de pacientes',
                'icon': 'fas fa-user-injured',
                'order': 1
            },
            {
                'name': 'DOCTOR',
                'url': '/core/doctor_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Registro de médicos',
                'icon': 'fas fa-user-md',
                'order': 2
            },
            {
                'name': 'ESPECIALIDAD',
                'url': '/core/especialidad_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Catálogo de especialidades médicas',
                'icon': 'fas fa-stethoscope',
                'order': 3
            },
            {
                'name': 'DIAGNOSTICO',
                'url': '/core/diagnostico_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Catálogo de diagnósticos',
                'icon': 'fas fa-diagnoses',
                'order': 4
            },
            {
                'name': 'ATENCION MEDICA',
                'url': '/doctor/atencion_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Registro de atenciones médicas',
                'icon': 'fas fa-heartbeat',
                'order': 5
            },
            {
                'name': 'CITA MEDICA',
                'url': '/doctor/cita_medica_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Programación de citas médicas',
                'icon': 'fas fa-calendar-check',
                'order': 6
            },
            {
                'name': 'SERVICIOS ADICIONALES',
                'url': '/doctor/servicios_adicionales_list/',
                'menu_name': 'GESTIÓN CLÍNICA',
                'description': 'Catálogo de servicios adicionales',
                'icon': 'fas fa-plus-circle',
                'order': 7
            },
            
            # FARMACIA Y MEDICAMENTOS
            {
                'name': 'MEDICAMENTOS',
                'url': '/core/medicamento_list/',
                'menu_name': 'FARMACIA Y MEDICAMENTOS',
                'description': 'Catálogo de medicamentos',
                'icon': 'fas fa-pills',
                'order': 1
            },
            {
                'name': 'TIPO DE MEDICAMENTO',
                'url': '/core/tipo_medicamento_list/',
                'menu_name': 'FARMACIA Y MEDICAMENTOS',
                'description': 'Clasificación de medicamentos',
                'icon': 'fas fa-layer-group',
                'order': 2
            },
            {
                'name': 'MARCA DE MEDICAMENTO',
                'url': '/core/marca_medicamento_list/',
                'menu_name': 'FARMACIA Y MEDICAMENTOS',
                'description': 'Marcas de medicamentos',
                'icon': 'fas fa-trademark',
                'order': 3
            },
            
            # LABORATORIO CLÍNICO
            {
                'name': 'TIPO DE SANGRE',
                'url': '/core/tipo_sangre_list/',
                'menu_name': 'LABORATORIO CLÍNICO',
                'description': 'Catálogo de tipos de sangre',
                'icon': 'fas fa-tint',
                'order': 1
            },
            
            # RECURSOS HUMANOS
            {
                'name': 'CARGO',
                'url': '/core/cargo_list/',
                'menu_name': 'RECURSOS HUMANOS',
                'description': 'Catálogo de cargos',
                'icon': 'fas fa-briefcase',
                'order': 1
            },
            {
                'name': 'EMPLEADOS',
                'url': '/core/empleado_list/',
                'menu_name': 'RECURSOS HUMANOS',
                'description': 'Registro de empleados',
                'icon': 'fas fa-id-badge',
                'order': 2
            },
            {
                'name': 'HORARIO DE ATENCION',
                'url': '/doctor/horario_atencion_list/',
                'menu_name': 'RECURSOS HUMANOS',
                'description': 'Horarios de atención médica',
                'icon': 'fas fa-clock',
                'order': 3
            }
        ]
        
        for module_data in modules_data:
            try:
                menu = Menu.objects.get(name=module_data['menu_name'])
                module, created = Module.objects.get_or_create(
                    name=module_data['name'],
                    defaults={
                        'url': module_data['url'],
                        'menu': menu,
                        'description': module_data['description'],
                        'icon': module_data['icon'],
                        'order': module_data['order'],
                        'is_active': True
                    }
                )
                if created:
                    self.created_count['modules'] += 1
                    print(f"  ✅ Creado: {module.name} ({menu.name})")
                else:
                    # Actualizar si es necesario
                    updated = False
                    if module.url != module_data['url']:
                        module.url = module_data['url']
                        updated = True
                    if module.description != module_data['description']:
                        module.description = module_data['description']
                        updated = True
                    if module.icon != module_data['icon']:
                        module.icon = module_data['icon']
                        updated = True
                    if module.order != module_data['order']:
                        module.order = module_data['order']
                        updated = True
                    if updated:
                        module.save()
                        self.updated_count['modules'] += 1
                        print(f"  🔄 Actualizado: {module.name}")
                    else:
                        print(f"  ✓ Ya existe: {module.name}")
            except Menu.DoesNotExist:
                print(f"  ❌ Error: Menú '{module_data['menu_name']}' no encontrado para módulo '{module_data['name']}'")
    
    def create_groups(self):
        """Crear todos los grupos del sistema"""
        print("\n👥 Creando/actualizando grupos...")
        
        groups_data = [
            'Administradores',
            'Doctores',
            'Secretaria',
            'Laboratorista',
            'Enfermeros',
            'Farmaceuticos'
        ]
        
        for group_name in groups_data:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.created_count['groups'] += 1
                print(f"  ✅ Creado: {group.name}")
            else:
                print(f"  ✓ Ya existe: {group.name}")
    
    def create_group_module_permissions(self):
        """Crear todas las asignaciones de permisos grupo-módulo"""
        print("\n🔐 Creando/actualizando permisos grupo-módulo...")
        
        # Definir los permisos por grupo y módulo
        permissions_data = [
            # ADMINISTRADORES - Todos los permisos en todos los módulos
            {
                'group_name': 'Administradores',
                'module_permissions': {
                    # Administración del Sistema
                    'USUARIOS': ['add_user', 'change_user', 'delete_user', 'view_user'],
                    'MODULOS': ['add_module', 'change_module', 'delete_module', 'view_module'],
                    'MENUS': ['add_menu', 'change_menu', 'delete_menu', 'view_menu'],
                    'GRUPOS MODULOS': ['add_groupmodulepermission', 'change_groupmodulepermission', 'delete_groupmodulepermission', 'view_groupmodulepermission'],
                    'GRUPOS': ['add_group', 'change_group', 'delete_group', 'view_group'],
                    
                    # Gestión Clínica
                    'PACIENTES': ['add_paciente', 'change_paciente', 'delete_paciente', 'view_paciente'],
                    'DOCTOR': ['add_doctor', 'change_doctor', 'delete_doctor', 'view_doctor'],
                    'ESPECIALIDAD': ['add_especialidad', 'change_especialidad', 'delete_especialidad', 'view_especialidad'],
                    'DIAGNOSTICO': ['add_diagnostico', 'change_diagnostico', 'delete_diagnostico', 'view_diagnostico'],
                    'ATENCION MEDICA': ['add_atencion', 'change_atencion', 'delete_atencion', 'view_atencion'],
                    'CITA MEDICA': ['add_citamedica', 'change_citamedica', 'delete_citamedica', 'view_citamedica'],
                    'SERVICIOS ADICIONALES': ['add_serviciosadicionales', 'change_serviciosadicionales', 'delete_serviciosadicionales', 'view_serviciosadicionales'],
                    
                    # Farmacia y Medicamentos
                    'MEDICAMENTOS': ['add_medicamento', 'change_medicamento', 'delete_medicamento', 'view_medicamento'],
                    'TIPO DE MEDICAMENTO': ['add_tipomedicamento', 'change_tipomedicamento', 'delete_tipomedicamento', 'view_tipomedicamento'],
                    'MARCA DE MEDICAMENTO': ['add_marcamedicamento', 'change_marcamedicamento', 'delete_marcamedicamento', 'view_marcamedicamento'],
                    
                    # Laboratorio Clínico
                    'TIPO DE SANGRE': ['add_tiposangre', 'change_tiposangre', 'delete_tiposangre', 'view_tiposangre'],
                    
                    # Recursos Humanos
                    'CARGO': ['add_cargo', 'change_cargo', 'delete_cargo', 'view_cargo'],
                    'EMPLEADOS': ['add_empleado', 'change_empleado', 'delete_empleado', 'view_empleado'],
                    'HORARIO DE ATENCION': ['add_horarioatencion', 'change_horarioatencion', 'delete_horarioatencion', 'view_horarioatencion'],
                    
                    # Gastos y Facturación
                    'PAGOS': ['add_pago', 'change_pago', 'delete_pago', 'view_pago'],
                    'TIPO DE GASTO': ['add_tipogasto', 'change_tipogasto', 'delete_tipogasto', 'view_tipogasto'],
                    'GASTOS MENSUALES': ['add_gastomensual', 'change_gastomensual', 'delete_gastomensual', 'view_gastomensual']
                }
            },
            
            # DOCTORES
            {
                'group_name': 'Doctores',
                'module_permissions': {
                    'PACIENTES': ['add_paciente', 'change_paciente', 'view_paciente'],
                    'ESPECIALIDAD': ['view_especialidad'],
                    'DIAGNOSTICO': ['add_diagnostico', 'change_diagnostico', 'view_diagnostico'],
                    'ATENCION MEDICA': ['add_atencion', 'change_atencion', 'view_atencion'],
                    'CITA MEDICA': ['add_citamedica', 'change_citamedica', 'view_citamedica'],
                    'SERVICIOS ADICIONALES': ['add_serviciosadicionales', 'change_serviciosadicionales', 'view_serviciosadicionales'],
                    'MEDICAMENTOS': ['view_medicamento'],
                    'TIPO DE MEDICAMENTO': ['view_tipomedicamento'],
                    'MARCA DE MEDICAMENTO': ['view_marcamedicamento'],
                    'TIPO DE SANGRE': ['view_tiposangre'],
                    'PAGOS': ['add_pago', 'change_pago', 'view_pago']
                }
            },
            
            # SECRETARIA
            {
                'group_name': 'Secretaria',
                'module_permissions': {
                    'PACIENTES': ['add_paciente', 'change_paciente', 'view_paciente'],
                    'CITA MEDICA': ['add_citamedica', 'change_citamedica', 'view_citamedica'],
                    'ESPECIALIDAD': ['view_especialidad'],
                    'DOCTOR': ['view_doctor'],
                    'CARGO': ['view_cargo'],
                    'ATENCION MEDICA': ['view_atencion'],
                    'PAGOS': ['view_pago']
                }
            },
            
            # LABORATORISTA
            {
                'group_name': 'Laboratorista',
                'module_permissions': {
                    'ATENCION MEDICA': ['change_atencion', 'view_atencion'],
                    'DIAGNOSTICO': ['view_diagnostico'],
                    'TIPO DE MEDICAMENTO': ['view_tipomedicamento'],
                    'MARCA DE MEDICAMENTO': ['view_marcamedicamento'],
                    'MEDICAMENTOS': ['view_medicamento'],
                    'TIPO DE SANGRE': ['add_tiposangre', 'change_tiposangre', 'view_tiposangre'],
                    'PACIENTES': ['view_paciente']
                }
            },
            
            # ENFERMEROS
            {
                'group_name': 'Enfermeros',
                'module_permissions': {
                    'PACIENTES': ['view_paciente'],
                    'ATENCION MEDICA': ['view_atencion'],
                    'CITA MEDICA': ['view_citamedica'],
                    'MEDICAMENTOS': ['view_medicamento'],
                    'TIPO DE SANGRE': ['view_tiposangre']
                }
            },
            
            # FARMACEUTICOS
            {
                'group_name': 'Farmaceuticos',
                'module_permissions': {
                    'MEDICAMENTOS': ['add_medicamento', 'change_medicamento', 'view_medicamento'],
                    'TIPO DE MEDICAMENTO': ['add_tipomedicamento', 'change_tipomedicamento', 'view_tipomedicamento'],
                    'MARCA DE MEDICAMENTO': ['add_marcamedicamento', 'change_marcamedicamento', 'view_marcamedicamento'],
                    'ATENCION MEDICA': ['view_atencion'],
                    'PACIENTES': ['view_paciente']
                }
            }
        ]
        
        for group_data in permissions_data:
            try:
                group = Group.objects.get(name=group_data['group_name'])
                
                for module_name, permission_codes in group_data['module_permissions'].items():
                    try:
                        module = Module.objects.get(name=module_name)
                        
                        # Crear o actualizar GroupModulePermission
                        gmp, created = GroupModulePermission.objects.get_or_create(
                            group=group,
                            module=module
                        )
                        
                        # Obtener permisos válidos
                        valid_permissions = []
                        for perm_code in permission_codes:
                            try:
                                permission = Permission.objects.get(codename=perm_code)
                                valid_permissions.append(permission)
                            except Permission.DoesNotExist:
                                print(f"    ⚠️ Permiso '{perm_code}' no encontrado")
                        
                        # Asignar permisos
                        if valid_permissions:
                            gmp.permissions.set(valid_permissions)
                            
                            if created:
                                self.created_count['group_module_permissions'] += 1
                                print(f"  ✅ Creado: {group.name} - {module.name} ({len(valid_permissions)} permisos)")
                            else:
                                self.updated_count['group_module_permissions'] += 1
                                print(f"  🔄 Actualizado: {group.name} - {module.name} ({len(valid_permissions)} permisos)")
                        
                    except Module.DoesNotExist:
                        print(f"  ❌ Módulo '{module_name}' no encontrado")
                        
            except Group.DoesNotExist:
                print(f"  ❌ Grupo '{group_data['group_name']}' no encontrado")
    
    def create_superuser_if_not_exists(self):
        """Crear superusuario si no existe"""
        print("\n👑 Verificando superusuario...")
        
        if not User.objects.filter(is_superuser=True).exists():
            print("  📝 No se encontró superusuario. Creando uno...")
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@sistema.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            print(f"  ✅ Superusuario creado: {superuser.username}")
            print(f"     Email: {superuser.email}")
            print(f"     Contraseña: admin123")
        else:
            print("  ✓ Ya existe al menos un superusuario")
    
    def assign_admin_to_administrators_group(self):
        """Asignar superusuarios al grupo Administradores"""
        print("\n🔗 Asignando superusuarios al grupo Administradores...")
        
        try:
            admin_group = Group.objects.get(name='Administradores')
            superusers = User.objects.filter(is_superuser=True)
            
            for superuser in superusers:
                if admin_group not in superuser.groups.all():
                    superuser.groups.add(admin_group)
                    print(f"  ✅ {superuser.username} agregado al grupo Administradores")
                else:
                    print(f"  ✓ {superuser.username} ya está en el grupo Administradores")
                    
        except Group.DoesNotExist:
            print("  ❌ Grupo 'Administradores' no encontrado")
    
    def print_summary(self):
        """Imprimir resumen de la ejecución"""
        print("\n" + "="*80)
        print("📊 RESUMEN DE LA EJECUCIÓN")
        print("="*80)
        print(f"✅ Menús creados: {self.created_count['menus']}")
        print(f"🔄 Menús actualizados: {self.updated_count['menus']}")
        print(f"✅ Módulos creados: {self.created_count['modules']}")
        print(f"🔄 Módulos actualizados: {self.updated_count['modules']}")
        print(f"✅ Grupos creados: {self.created_count['groups']}")
        print(f"🔄 Grupos actualizados: {self.updated_count['groups']}")
        print(f"✅ Permisos grupo-módulo creados: {self.created_count['group_module_permissions']}")
        print(f"🔄 Permisos grupo-módulo actualizados: {self.updated_count['group_module_permissions']}")
        print("="*80)
        
        # Estadísticas finales
        print("\n📈 ESTADÍSTICAS FINALES:")
        print(f"   🗂️ Total menús: {Menu.objects.count()}")
        print(f"   📁 Total módulos: {Module.objects.count()}")
        print(f"   👥 Total grupos: {Group.objects.count()}")
        print(f"   🔐 Total permisos grupo-módulo: {GroupModulePermission.objects.count()}")
        print(f"   👤 Total usuarios: {User.objects.count()}")
        print(f"   🔑 Total permisos disponibles: {Permission.objects.count()}")
    
    @transaction.atomic
    def run(self):
        """Ejecutar todo el proceso de creación/actualización"""
        print("🚀 INICIANDO CREACIÓN/ACTUALIZACIÓN DE ESTRUCTURA DE SEGURIDAD")
        print("="*80)
        
        try:
            self.create_menus()
            self.create_modules()
            self.create_groups()
            self.create_group_module_permissions()
            self.create_superuser_if_not_exists()
            self.assign_admin_to_administrators_group()
            self.print_summary()
            
            print("\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
            
        except Exception as e:
            print(f"\n❌ ERROR EN EL PROCESO: {str(e)}")
            raise


def main():
    """Función principal"""
    seeder = SecurityDataSeeder()
    seeder.run()


if __name__ == "__main__":
    main()
