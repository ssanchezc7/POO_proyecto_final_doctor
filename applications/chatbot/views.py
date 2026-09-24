from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import View
import json

from .models import ChatConversation, ChatMessage
from .services.gemini_service import GeminiChatService


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ChatAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
            
            if not message:
                return JsonResponse({'error': 'El mensaje no puede estar vacío'}, status=400)
            
            # Obtener o crear conversación
            if conversation_id:
                try:
                    conversation = ChatConversation.objects.get(
                        id=conversation_id, 
                        user=request.user
                    )
                except ChatConversation.DoesNotExist:
                    conversation = ChatConversation.objects.create(
                        user=request.user,
                        title=message[:50] + "..." if len(message) > 50 else message
                    )
            else:
                conversation = ChatConversation.objects.create(
                    user=request.user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
            
            # Generar respuesta con Gemini
            gemini_service = GeminiChatService()
            response_data = gemini_service.generate_response(message)
            
            # Guardar mensaje y respuesta
            chat_message = ChatMessage.objects.create(
                conversation=conversation,
                message=message,
                response=response_data['response']
            )
            
            return JsonResponse({
                'success': True,
                'response': response_data['response'],
                'conversation_id': conversation.id,
                'message_id': chat_message.id,
                'context': response_data.get('context', {})
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class ConversationHistoryView(View):
    def get(self, request, conversation_id):
        try:
            conversation = ChatConversation.objects.get(
                id=conversation_id, 
                user=request.user
            )
            
            messages = conversation.messages.all()
            
            history = []
            for message in messages:
                history.append({
                    'id': message.id,
                    'message': message.message,
                    'response': message.response,
                    'created_at': message.created_at.isoformat()
                })
            
            return JsonResponse({
                'success': True,
                'conversation_title': conversation.title,
                'history': history
            })
            
        except ChatConversation.DoesNotExist:
            return JsonResponse({'error': 'Conversación no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
