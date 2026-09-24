from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/conversation/<int:conversation_id>/', views.ConversationHistoryView.as_view(), name='conversation_history'),
]
