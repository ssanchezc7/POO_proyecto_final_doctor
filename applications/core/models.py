import os
from datetime import date
from django.core.validators import RegexValidator
from django.db import models
from applications.core.utils.medicamento import ViaAdministracion
from applications.core.utils.paciente import EstadoCivilChoices, SexoChoices
from proy_clinico.util import valida_cedula, valida_ruc
from django.utils import timezone

"""Modelo que representa los diferentes tipos de sangre."""
class TipoSangre(models.Model):
    tipo = models.CharField(max_length=10, verbose_name="Tipo de Sangre", unique=True)
    descripcion = models.CharField(max_length=100, verbose_name="Descripcion")

    class Meta:
        # Nombre en singular y plural del modelo en la interfaz de administración
        verbose_name = "Tipo de Sangre"
        verbose_name_plural = "Tipos de Sangre"

    def __str__(self):
        return self.tipo

""" Manager del modelo paciente """
class ActivePatientManager(models.Manager):
    # Método para obtener un queryset de pacientes activos
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)

""" Modelo que representa a los pacientes de la clínica. """
class Paciente(models.Model):
    # Información personal
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    cedula_ecuatoriana = models.CharField(
        max_length=10,
        verbose_name="Cédula",
        validators=[valida_cedula],
        help_text="Ingrese el número de cédula sin espacios ni guiones."
    )
    dni = models.CharField(
        max_length=30,
        verbose_name="Dni internacional",
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^[A-Za-z0-9\-\. ]{5,30}$',message="Ingrese un documento válido (letras, números, guiones o puntos)."
        )],
        help_text="Pasaporte, DNI, CURP u otro documento válido internacionalmente."
    )
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de Nacimiento",
        help_text="Formato: AAAA-MM-DD"
    )
    telefono = models.CharField(
        max_length=50,
        verbose_name="Teléfono(s)",
        help_text="Puede ingresar uno o más números separados por coma."
    )
    email = models.EmailField(
        verbose_name="Correo",
        null=True,
        blank=True,
        unique=True,
        help_text="Correo electrónico del paciente (opcional)."
    )
    sexo = models.CharField(max_length=10, choices=SexoChoices.choices, verbose_name="Sexo",default=SexoChoices.MASCULINO)
    estado_civil = models.CharField(max_length=12, choices=EstadoCivilChoices.choices, verbose_name="Estado Civil")
    direccion = models.CharField(max_length=255, verbose_name="Dirección Domiciliaria")
    latitud = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        verbose_name="Latitud",
        null=True,
        blank=True,
        help_text="Coordenada geográfica (opcional)."
    )
    longitud = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        verbose_name="Longitud",
        null=True,
        blank=True,
        help_text="Coordenada geográfica (opcional)."
    )
    tipo_sangre = models.ForeignKey(
        TipoSangre,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Tipo de Sangre",
        related_name="tipos_sangre",
        help_text="Ej.: O+, A-, B+, AB-"
    )
    foto = models.ImageField(
        upload_to='core/pacientes/',
        verbose_name="Foto",
        null=True,
        blank=True,
        help_text="Imagen de perfil del paciente (opcional)."
    )
    # === Historia Clínica ===
    # Enfermedades previas diagnosticadas por un médico.
    # Ejemplo: "Diabetes tipo 2 desde hace 5 años, hipertensión controlada"
    antecedentes_personales = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antecedentes personales patológicos",
        help_text="Ej.: Diabetes tipo 2, hipertensión, asma, etc."
    )
    # Cirugías o procedimientos importantes en el pasado.
    # Ejemplo: "Apendicectomía en 2018, cesárea en 2021"
    antecedentes_quirurgicos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antecedentes quirúrgicos",
        help_text="Ej.: Cirugías previas como apendicectomía, cesárea, etc."
    )
    # Enfermedades hereditarias o crónicas en la familia (padres, abuelos, hermanos).
    # Ejemplo: "Padre con diabetes, madre con hipertensión"
    antecedentes_familiares = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antecedentes familiares",
        help_text="Enfermedades hereditarias (padres, abuelos, hermanos)."
    )
    # Reacciones alérgicas a medicamentos, alimentos o sustancias.
    # Ejemplo: "Alergia a la penicilina y mariscos"
    alergias = models.TextField(
        blank=True,
        null=True,
        verbose_name="Alergias",
        help_text="Ej.: Penicilina, mariscos, polvo, etc."
    )
    # Medicamentos que el paciente toma actualmente, con dosis y frecuencia.
    # Ejemplo: "Metformina 850mg cada 12 horas, Losartán 50mg diario"
    medicamentos_actuales = models.TextField(
        blank=True,
        null=True,
        verbose_name="Medicamentos actuales",
        help_text="Nombre, dosis y frecuencia. Ej.: Losartán 50mg diario."
    )
    # Registro de hábitos que puedan afectar la salud del paciente.
    # Ejemplo: "tabaco", "alcohol", "drogas", "sedentarismo"
    habitos_toxicos = models.CharField(
        max_length=200,
        default='ninguno',
        verbose_name="Hábitos tóxicos o perjudiciales",
        help_text="Ej.: Tabaco, alcohol, drogas, sedentarismo, etc."
    )
    # Información sobre vacunas recientes o estado general de vacunación.
    # Ejemplo: "Vacunado contra COVID-19 (última dosis en 2023), influenza anual"
    vacunas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Vacunas",
        help_text="Vacunas importantes recibidas. Ej.: COVID-19, influenza, etc."
    )
    # Información gineco-obstétrica, solo para mujeres en edad fértil.
    # Ejemplo: "G2P1A1, menarquia a los 12 años, usa anticonceptivos orales"
    antecedentes_gineco_obstetricos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antecedentes gineco-obstétricos",
        help_text="Solo en mujeres. Ej.: menarquia, embarazos, anticonceptivos."
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    objects = models.Manager()  # Manager predeterminado
    active_patient = ActivePatientManager()  # Manager Personalizado

    class Meta:
        ordering = ['apellidos']
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.apellidos} {self.nombres}"

    @property
    def get_image(self):
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url
        return '/static/img/usuario_anonimo.png'

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        today = date.today()
        edad = today.year - self.fecha_nacimiento.year
        if (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad

    @staticmethod
    def cantidad_pacientes():
        return Paciente.objects.count()

"""Modelo que representa las diferentes especialidades médicas.
Cada doctor puede tener una o varias especialidades.
"""
class Especialidad(models.Model):
    # Nombre de la especialidad médica (ej. Cardiología, Pediatría, etc.)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Especialidad",
        help_text="Ejemplo: Cardiología, Pediatría, Ginecología"
    )

    # Descripción opcional de la especialidad
    descripcion = models.TextField(
        verbose_name="Descripción",
        null=True,
        blank=True,
        help_text="Breve explicación o enfoque de la especialidad (opcional)."
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Marcar como inactivo para ocultar esta especialidad en el sistema."
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = "Especialidad médica"
        verbose_name_plural = "Especialidades médicas"

    def __str__(self):
        return self.nombre

# Modelo que representa a los doctores que trabajan en la clínica.
# Almacena información personal, profesional, y detalles importantes
# como su especialidad, curriculum y datos médicos adicionales.
class Doctor(models.Model):
    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres"
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos"
    )
    ruc = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="Ruc",
        validators=[valida_ruc],
        help_text="Ingrese un RUC válido (persona natural, sociedad o extranjero)."

    )
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de Nacimiento"
    )
    direccion = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Dirección de Trabajo",
        help_text="Ubicación física donde atiende el doctor."
    )
    latitud = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        verbose_name="Latitud",
        null=True,
        blank=True,
        help_text="Coordenada GPS (opcional)."
    )
    longitud = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        verbose_name="Longitud",
        null=True,
        blank=True,
        help_text="Coordenada GPS (opcional)."
    )
    codigo_unico_doctor = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código Único del Doctor",
        help_text="Identificador interno único para el doctor."
    )
    especialidad = models.ManyToManyField(
        'Especialidad',
        verbose_name="Especialidades",
        related_name="especialidades",
        help_text="Seleccione una o más especialidades médicas."
    )
    telefonos = models.CharField(
        max_length=20,
        verbose_name="Teléfonos",
        help_text="Número de contacto. Puede ser celular o fijo."
    )
    email = models.EmailField(
        verbose_name="Correo Electrónico",
        null=True,
        blank=True,
        help_text="Correo de contacto (opcional)."
    )
    horario_atencion = models.TextField(
        verbose_name="Horario de Atención",
        help_text="Ejemplo: Lunes a Viernes, 08h00 - 13h00"
    )
    horarios_atencion = models.ManyToManyField(
        'doctor.HorarioAtencion',
        verbose_name="Horarios de Atención",
        related_name="doctores",
        blank=True,
        help_text="Horarios predefinidos seleccionables"
    )
    duracion_atencion = models.PositiveIntegerField(
        verbose_name="Duración de Cita (minutos)",
        default=30,
        help_text="Tiempo estándar asignado a cada paciente."
    )
    curriculum = models.FileField(
        upload_to='core/curriculums/',
        verbose_name="Currículum Vitae",
        null=True,
        blank=True,
        help_text="Archivo PDF o DOC (opcional)."
    )
    firma_digital = models.ImageField(
        upload_to='core/firmas/',
        verbose_name="Firma Digital",
        null=True,
        blank=True,
        help_text="Imagen que será usada para firmar digitalmente."
    )
    foto = models.ImageField(
        upload_to='core/doctores/',
        verbose_name="Foto",
        null=True,
        blank=True
    )
    imagen_receta = models.ImageField(
        upload_to='core/recetas/',
        verbose_name="Imagen para Recetas",
        null=True,
        blank=True,
        help_text="Encabezado o firma que se mostrará en recetas médicas."
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Si está desmarcado, el doctor no podrá ser asignado a consultas."
    )

    @property
    def nombre_completo(self):
        return f"{self.apellidos} {self.nombres}"

    def __str__(self):
        return self.nombre_completo

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"
        ordering = ['apellidos', 'nombres']


# Modelo que representa los diferentes cargos que pueden tener los empleados en la clínica.
# Cada cargo puede tener un nombre y una descripción.
class Cargo(models.Model):
    # Nombre del cargo (ej. Médico, Enfermero, Administrador, etc.)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Cargo",
        help_text="Ej.: Médico, Enfermero, Administrador"
    )

    # Descripción del cargo (opcional)
    descripcion = models.TextField(
        verbose_name="Descripción del Cargo",
        null=True,
        blank=True,
        help_text="Descripción breve del rol que cumple este cargo (opcional)."
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Desactiva este cargo si ya no se usa en el sistema."
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nombre']  # Orden alfabético en listados del admin

# Modelo que representa a los empleados que trabajan en la clínica.
# Incluye información personal, profesional y datos de contacto.
class Empleado(models.Model):
    nombres = models.CharField(max_length=100, verbose_name="Nombre del Empleado")
    apellidos = models.CharField(max_length=100, verbose_name="Apellido del Empleado")
    cedula_ecuatoriana = models.CharField(
        max_length=10,
        verbose_name="Cédula",
        validators=[valida_cedula],
        help_text="Ingrese el número de cédula sin espacios ni guiones."
    )
    dni = models.CharField(
        max_length=30,
        verbose_name="Dni internacional",
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^[A-Za-z0-9\-\. ]{5,30}$',
                                   message="Ingrese un documento válido (letras, números, guiones o puntos)."
                                   )],
        help_text="Pasaporte, DNI, CURP u otro documento válido internacionalmente."
    )
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    cargo = models.ForeignKey('Cargo', on_delete=models.PROTECT, verbose_name="Cargo", related_name="cargos")
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sueldo")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    latitud = models.FloatField(verbose_name="Latitud", null=True, blank=True)
    longitud = models.FloatField(verbose_name="Longitud", null=True, blank=True)
    foto = models.ImageField(upload_to='core/empleados/', verbose_name="Foto del Empleado", null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")

    @property
    def nombre_completo(self):
        return f"{self.apellidos} {self.nombres}"

    def __str__(self):
        return self.nombre_completo

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

class TipoMedicamento(models.Model):
    # Nombre del tipo de medicamento (ej. Analgésico, Antibiótico, etc.)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tipo de Medicamento",
        help_text="Ejemplo: Analgésico, Antibiótico, Antiinflamatorio"
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        null=True,
        blank=True,
        help_text="Información adicional sobre este tipo de medicamento."
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Medicamento"
        verbose_name_plural = "Tipos de Medicamentos"
        ordering = ['nombre']


class MarcaMedicamento(models.Model):
    # Nombre de la marca (ej. Pfizer, Bayer, Novartis)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Marca de Medicamento",
        help_text="Nombre de la marca comercial. Ejemplo: Pfizer, Bayer, Novartis"
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        null=True,
        blank=True,
        help_text="Descripción general u observaciones sobre esta marca."
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Marca de Medicamento"
        verbose_name_plural = "Marcas de Medicamentos"
        ordering = ['nombre']


class ActiveMedicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)


class Medicamento(models.Model):
    tipo = models.ForeignKey(
        TipoMedicamento,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Medicamento",
        related_name="medicamentos_por_tipo"
    )
    marca_medicamento = models.ForeignKey(
        MarcaMedicamento,
        on_delete=models.PROTECT,
        verbose_name="Marca",
        related_name="medicamentos_por_marca",
        null=True,
        blank=True
    )
    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Nombre del Medicamento",
        help_text="Nombre comercial o genérico. Ejemplo: Ibuprofeno"
    )
    descripcion = models.TextField(
        verbose_name="Descripción del Medicamento",
        null=True,
        blank=True,
        help_text="Uso, indicaciones o precauciones relevantes."
    )
    concentracion = models.CharField(
        max_length=50,
        verbose_name="Concentración",
        null=True,
        blank=True,
        help_text="Ejemplo: 500mg, 1g, 5%"
    )
    via_administracion = models.CharField(
        max_length=20,
        choices=ViaAdministracion.choices,
        verbose_name="Vía de Administración",
        help_text="Forma en que se administra el medicamento (oral, intravenosa, etc.)"
    )
    cantidad = models.PositiveIntegerField(
        verbose_name="Stock",
        help_text="Cantidad actual disponible en inventario."
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio",
        help_text="Precio unitario del medicamento."
    )
    comercial = models.BooleanField(
        default=True,
        verbose_name="Comercial",
        help_text="Marcar como 'No' si es un medicamento genérico."
    )

    foto = models.ImageField(upload_to='core/medicamentos/', verbose_name="Foto del Medicamento", null=True, blank=True)

    activo = models.BooleanField(default=True, verbose_name="Activo")

    objects = models.Manager()
    active_medication = ActiveMedicationManager()

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    class Meta:
        ordering = ['nombre']
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

# Modelo que representa los diagnósticos médicos.
# Incluye un código único, descripción y un campo adicional para información relevante.
class Diagnostico(models.Model):
    # Código único del diagnóstico (Ej.: CIE-10 A09, ICD-10 J00, etc.)
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código del Diagnóstico",
        help_text="Código estándar del diagnóstico (Ej: A09, J00, K35.2)"
    )

    # Descripción breve del diagnóstico (Ej.: Gastroenteritis viral, Rinitis aguda)
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción del Diagnóstico",
        help_text="Nombre del diagnóstico según el código (Ej.: Faringitis aguda)"
    )

    # Campo adicional para observaciones clínicas, notas o contexto específico
    datos_adicionales = models.TextField(
        null=True,
        blank=True,
        verbose_name="Datos Adicionales",
        help_text="Observaciones clínicas u otra información útil."
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Desactiva este diagnóstico si ya no está en uso."
    )

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"
        ordering = ["codigo"]  # orden alfabético por código

class TipoGasto(models.Model):
    """
    Modelo que define los tipos de gastos operativos del consultorio del doctor.
    Ejemplo: Arriendo, Luz, Agua, Internet, Insumos Médicos, etc.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Tipo de Gasto",
        help_text="Ejemplo: Arriendo, Luz, Agua, Internet, Insumos médicos, etc."
    )
    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción del Gasto",
        help_text="Detalle adicional sobre este tipo de gasto (opcional)."
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si este tipo de gasto está disponible para ser seleccionado."
    )

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = "Tipo de Gasto"
        verbose_name_plural = "Tipos de Gastos"


class GastoMensual(models.Model):
    """
    Modelo que registra los gastos mensuales del consultorio del doctor.
    """
    tipo_gasto = models.ForeignKey(
        TipoGasto,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Gasto",
        related_name="gastos_mensuales"
    )
    fecha = models.DateField(
        default=timezone.now,
        verbose_name="Fecha del Gasto",
        help_text="Fecha en que se incurrió el gasto."
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor del Gasto",
        help_text="Monto en dólares del gasto realizado."
    )
    observacion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observación",
        help_text="Comentario adicional sobre este gasto (opcional)."
    )

    def __str__(self):
        return f"{self.tipo_gasto} - {self.valor} ({self.fecha})"

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Gasto Mensual"
        verbose_name_plural = "Gastos Mensuales"


def ruta_foto_paciente(instance, filename):
    """
    Genera una ruta única por paciente para subir las fotos.
    Ejemplo: media/pacientes/123/foto_2025_06_15_154530.jpg
    """
    base, extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    return f"doctor/pacientes/{instance.paciente.id}/foto_{timestamp}{extension}"

class FotoPaciente(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="fotos",
        verbose_name="Paciente",
        help_text="Paciente al que pertenece esta imagen."
    )

    imagen = models.ImageField(
        upload_to=ruta_foto_paciente,
        verbose_name="Imagen del Paciente",
        help_text="Imagen relacionada con el paciente. Puede ser histórica o actual."
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción",
        help_text="Comentario opcional sobre la imagen (ej. cicatriz, antes/después, etc.)"
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Subida",
        help_text="Fecha en la que se subió la imagen."
    )

    class Meta:
        ordering = ['-fecha_subida']
        verbose_name = "Foto del Paciente"
        verbose_name_plural = "Fotos de los Pacientes"

    def __str__(self):
        return f"Foto de {self.paciente} ({self.fecha_subida.strftime('%Y-%m-%d %H:%M')})"