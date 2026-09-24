from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

class ChatConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")
    title = models.CharField(max_length=255, verbose_name="Título", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title or 'Conversación'}"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages', verbose_name="Conversación")
    message = models.TextField(verbose_name="Mensaje")
    response = models.TextField(verbose_name="Respuesta", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    
    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.conversation.user.username} - {self.message[:50]}"
