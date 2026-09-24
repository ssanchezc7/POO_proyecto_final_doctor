"""
Señales para el módulo de doctor
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetallePago


@receiver(post_save, sender=DetallePago)
def actualizar_total_pago_on_save(sender, instance, **kwargs):
    """
    Actualiza el total del pago cuando se guarda un detalle
    """
    if instance.pago:
        instance.pago.recalcular_total()
        instance.pago.save()


@receiver(post_delete, sender=DetallePago)
def actualizar_total_pago_on_delete(sender, instance, **kwargs):
    """
    Actualiza el total del pago cuando se elimina un detalle
    """
    if instance.pago:
        instance.pago.recalcular_total()
        instance.pago.save()
