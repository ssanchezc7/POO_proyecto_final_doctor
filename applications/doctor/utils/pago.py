from django.db import models

class MetodoPagoChoices(models.TextChoices):
    EFECTIVO = 'efectivo', 'Efectivo'
    PAYPAL = 'paypal', 'PayPal'
    TARJETA = 'tarjeta', 'Tarjeta de Crédito/Débito'
    TRANSFERENCIA = 'transferencia', 'Transferencia Bancaria'


class EstadoPagoChoices(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    PAGADO = 'pagado', 'Pagado'
    CANCELADO = 'cancelado', 'Cancelado'
    REEMBOLSADO = 'reembolsado', 'Reembolsado'