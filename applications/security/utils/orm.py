from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from applications.security.models import GroupModulePermission, Menu, Module, User

# Create Menus - using save() and create()
menu1 = Menu(
    name='Registros',
    icon='bi bi-person',
    order=7
)
menu1.save()

menu1 = Menu(
    name='Emergencia',
    icon='fa fa-person',
    order=7
)
menu1.save()

menu2 = Menu.objects.create(
    name='Consultas',
    icon='bi bi-calendar-check',
    order=2
)

menu3 = Menu.objects.create(
    name='Auditores',
    icon='bi bi-gear',
    order=4
)

# Create Modules using bulk_create
modules = [
    # Modules for Pacientes menu
    Module(url='pacientes/', name='Registro de Pacientes', menu_id=menu1.id,
           description='Gestión de información de pacientes', icon='bi bi-person-plus', order=1),
    Module(url='historial/', name='Historial Médico', menu=menu1, 
           description='Historial clínico de pacientes', icon='bi bi-file-medical', order=2),
    Module(url='seguimiento/', name='Seguimiento', menu=menu1, 
           description='Seguimiento de tratamientos y evolución', icon='bi bi-graph-up', order=3),
    
    # Modules for Consultas menu
    Module(url='citas/', name='Citas', menu=menu2, 
           description='Programación de citas médicas', icon='bi bi-calendar-date', order=1),
    Module(url='diagnosticos/', name='Diagnósticos', menu=menu2, 
           description='Registro de diagnósticos médicos', icon='bi bi-clipboard-pulse', order=2),
    Module(url='recetas/', name='Recetas', menu=menu2, 
           description='Emisión de recetas médicas', icon='bi bi-file-earmark-text', order=3),
    
    # Modules for Administración menu
    Module(url='usuarios/', name='Usuarios', menu=menu3, 
           description='Gestión de usuarios del sistema', icon='bi bi-people', order=1),
    Module(url='configuracion/', name='Configuración', menu=menu3, 
           description='Configuración general del sistema', icon='bi bi-sliders', order=2),
    Module(url='reportes/', name='Reportes', menu=menu3, 
           description='Generación de reportes y estadísticas', icon='bi bi-bar-chart', order=3)
]

created_modules = Module.objects.bulk_create(modules)
module1, module2, module3, module4, module5, module6, module7, module8, module9 = created_modules

# Create Users
user1 = User.objects.create(
    username='drgomez2',
    email='drgomezz@clinica.med',
    password='secure123!',
    first_name='Carlos',
    last_name='Gómez',
    dni='0912345678',
    direction='Av. Principal 123, Guayaquil',
    phone='0991234567',
    is_staff=True
)

user2 = User.objects.create(
    username='asistente',
    email='asistente@clinica.med',
    password='asist2025!',
    first_name='María',
    last_name='Sánchez',
    dni='0923456789',
    direction='Calle Secundaria 456, Guayaquil',
    phone='0982345678',
    is_staff=False
)

# Create Groups
group_medicos = Group.objects.create(name='Médicos')
group_asistentes = Group.objects.create(name='Asistentes')

# Add users to groups y si se usa set() se eliminan los grupos anteriores
user1.groups.add(group_medicos)
user2.groups.add(group_asistentes)

# Create permissions for Patient and Diagnosis models only
patient_ct = ContentType.objects.get(app_label='doctor', model='patient')
diagnosis_ct = ContentType.objects.get(app_label='doctor', model='diagnosis')

# Patient permissions.busca un objeto y, si no existe, lo crea automáticamente. Devueleve una tupla(objeto,encontrado).
patient_view_tupla = Permission.objects.get_or_create(codename='view_patient', name='Can view Paciente', content_type=patient_ct)
patient_view = Permission.objects.get_or_create(codename='view_patient', name='Can view Paciente', content_type=patient_ct)[0]
patient_add = Permission.objects.get_or_create(codename='add_patient', name='Can add Paciente', content_type=patient_ct)[0]
patient_change = Permission.objects.get_or_create(codename='change_patient', name='Can change Paciente', content_type=patient_ct)[0]
patient_delete = Permission.objects.get_or_create(codename='delete_patient', name='Can delete Paciente', content_type=patient_ct)[0]

# Diagnosis permissions
diagnosis_view = Permission.objects.get_or_create(codename='view_diagnosis', name='Can view Diagnóstico', content_type=diagnosis_ct)[0]
diagnosis_add = Permission.objects.get_or_create(codename='add_diagnosis', name='Can add Diagnóstico', content_type=diagnosis_ct)[0]
diagnosis_change = Permission.objects.get_or_create(codename='change_diagnosis', name='Can change Diagnóstico', content_type=diagnosis_ct)[0]
diagnosis_delete = Permission.objects.get_or_create(codename='delete_diagnosis', name='Can delete Diagnóstico', content_type=diagnosis_ct)[0]

# Add permissions to modules
module1.permissions.add(patient_view, patient_add, patient_change, patient_delete)
module5.permissions.add(diagnosis_view, diagnosis_add, diagnosis_change, diagnosis_delete)

# Create GroupModulePermission records
# For Médicos with Patient module
gmp1 = GroupModulePermission.objects.create(group=group_medicos, module=module1)
gmp1.permissions.add(patient_view, patient_add, patient_change, patient_delete)

# For Médicos with Diagnosis module
gmp2 = GroupModulePermission.objects.create(group=group_medicos, module=module5)
gmp2.permissions.add(diagnosis_view, diagnosis_add, diagnosis_change)

# For Asistentes with Patient module (limited permissions)
gmp3 = GroupModulePermission.objects.create(group=group_asistentes, module=module1)
gmp3.permissions.add(patient_view, patient_add)

# For Asistentes with Diagnosis module (view only)
gmp4 = GroupModulePermission.objects.create(group=group_asistentes, module=module5)
gmp4.permissions.add(diagnosis_view)

