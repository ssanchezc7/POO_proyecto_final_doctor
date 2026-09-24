from django.db import models


class DiaSemanaChoices(models.TextChoices):
    LUNES = 'lunes', 'Lunes'
    MARTES = 'martes', 'Martes'
    MIERCOLES = 'miércoles', 'Miércoles'
    JUEVES = 'jueves', 'Jueves'
    VIERNES = 'viernes', 'Viernes'
    SABADO = 'sábado', 'Sábado'
    DOMINGO = 'domingo', 'Domingo'