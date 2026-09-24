from applications.chatbot.models import ChatConversation

def chatbot_context(request):
    """Context processor para el widget de chatbot"""
    context = {}
    
    if request.user.is_authenticated:
        # Obtener las últimas conversaciones del usuario
        recent_conversations = ChatConversation.objects.filter(
            user=request.user
        ).order_by('-updated_at')[:5]
        
        context['chatbot_conversations'] = recent_conversations
        context['chatbot_enabled'] = True
    else:
        context['chatbot_enabled'] = False
    
    return context
