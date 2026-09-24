from django.core.management.base import BaseCommand
from applications.chatbot.services.gemini_service import GeminiChatService


class Command(BaseCommand):
    help = 'Prueba la conexión con la API de Gemini'

    def handle(self, *args, **options):
        try:
            service = GeminiChatService()
            response = service.generate_response("Hola, ¿cómo estás?")
            
            if response['success']:
                self.stdout.write(
                    self.style.SUCCESS('✓ Conexión exitosa con Gemini API')
                )
                self.stdout.write(f"Respuesta: {response['response']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error: {response["error"]}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error de conexión: {str(e)}')
            )
