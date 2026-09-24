from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from applications.core.models import Doctor


class Command(BaseCommand):
    help = 'Crear grupo de Doctores con permisos básicos'

    def handle(self, *args, **options):
        # Crear o obtener el grupo de doctores
        group, created = Group.objects.get_or_create(name='Doctores')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Doctores" creado exitosamente.'))
        else:
            self.stdout.write(self.style.WARNING('El grupo "Doctores" ya existe.'))

        # Obtener content type para Doctor
        try:
            doctor_content_type = ContentType.objects.get_for_model(Doctor)
            
            # Permisos básicos para doctores
            basic_permissions = [
                'view_doctor',
                'change_doctor',  # Para que puedan editar su propio perfil
            ]
            
            # Agregar permisos al grupo
            for perm_codename in basic_permissions:
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=doctor_content_type
                    )
                    group.permissions.add(permission)
                    self.stdout.write(f'Permiso "{perm_codename}" agregado al grupo Doctores.')
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Permiso "{perm_codename}" no encontrado.')
                    )
            
            # Agregar permisos adicionales que podrían necesitar los doctores
            try:
                # Permisos para ver pacientes
                from applications.core.models import Paciente
                paciente_ct = ContentType.objects.get_for_model(Paciente)
                paciente_perms = ['view_paciente']
                
                for perm_codename in paciente_perms:
                    try:
                        permission = Permission.objects.get(
                            codename=perm_codename,
                            content_type=paciente_ct
                        )
                        group.permissions.add(permission)
                        self.stdout.write(f'Permiso "{perm_codename}" agregado al grupo Doctores.')
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'Permiso "{perm_codename}" no encontrado.')
                        )
            except:
                pass
            
            self.stdout.write(
                self.style.SUCCESS('Configuración del grupo "Doctores" completada.')
            )
                
        except ContentType.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('ContentType para Doctor no encontrado. Ejecute primero las migraciones.')
            )
