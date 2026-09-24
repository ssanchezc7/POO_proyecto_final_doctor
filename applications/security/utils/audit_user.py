from django.db import models

class AccionChoices(models.TextChoices):
    ADICION = 'ADICION', 'ADICION'
    MODIFICACION = 'MODIFICACION', 'MODIFICACION'
    ELIMINACION = 'ELIMINACION', 'ELIMINACION'