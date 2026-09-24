from django.db import models


class SexoChoices(models.TextChoices):
    MASCULINO = 'masculino', 'Masculino'
    FEMENINO = 'femenino', 'Femenino'

class EstadoCivilChoices(models.TextChoices):
    SOLTERO = 'soltero', 'Soltero'
    CASADO = 'casado', 'Casado'
    DIVORCIADO = 'divorciado', 'Divorciado'
    VIUDO = 'viudo', 'Viudo'
    UNION_LIBRE = 'union_libre', 'Unión libre'