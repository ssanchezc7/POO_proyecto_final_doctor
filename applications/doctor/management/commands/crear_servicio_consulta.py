from django.core.management.base import BaseCommand
from decimal import Decimal
from applications.doctor.models import ServiciosAdicionales


class Command(BaseCommand):
    help = 'Crea el servicio adicional de "Consulta Médica" si no existe'

    def handle(self, *args, **options):
        servicio, created = ServiciosAdicionales.objects.get_or_create(
            nombre_servicio="Consulta Médica",
            defaults={
                'costo_servicio': Decimal('25.00'),
                'descripcion': 'Consulta médica general - Servicio base para facturación automática',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Servicio "Consulta Médica" creado exitosamente con costo ${servicio.costo_servicio}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ El servicio "Consulta Médica" ya existe con costo ${servicio.costo_servicio}'
                )
            )
        
        # Mostrar información del servicio
        self.stdout.write(f'ID: {servicio.id}')
        self.stdout.write(f'Nombre: {servicio.nombre_servicio}')
        self.stdout.write(f'Costo: ${servicio.costo_servicio}')
        self.stdout.write(f'Activo: {servicio.activo}')
        self.stdout.write(f'Descripción: {servicio.descripcion}')
