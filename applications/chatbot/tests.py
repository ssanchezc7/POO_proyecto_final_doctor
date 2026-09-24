from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from applications.chatbot.models import ChatConversation, ChatMessage

User = get_user_model()

class ChatbotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
    
    def test_chatbot_view_accessible(self):
        """Test que la vista del chatbot es accesible"""
        response = self.client.get(reverse('chatbot:chatbot'))
        self.assertEqual(response.status_code, 200)
    
    def test_chat_conversation_creation(self):
        """Test que se puede crear una conversación"""
        conversation = ChatConversation.objects.create(
            user=self.user,
            title="Test Conversation"
        )
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.title, "Test Conversation")
    
    def test_chat_message_creation(self):
        """Test que se puede crear un mensaje"""
        conversation = ChatConversation.objects.create(
            user=self.user,
            title="Test Conversation"
        )
        message = ChatMessage.objects.create(
            conversation=conversation,
            message="Test message",
            response="Test response"
        )
        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.message, "Test message")
        self.assertEqual(message.response, "Test response")
