from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from faqs.models import FAQ
from .models import ChatSession, ChatMessage

User = get_user_model()


class ChatbotAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chat_user', password='StrongPass123!')
        self.other = User.objects.create_user(username='chat_other', password='StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.user).access_token}')
        self.faq = FAQ.objects.create(question='How can I reset my password?', answer='Use the password reset link.', is_published=True)
        FAQ.objects.create(question='Unpublished internal procedure', answer='Do not expose this.', is_published=False)

    @patch('ai_services.chat_views.generate_chat_answer', return_value='Use the password reset link.')
    def test_chatbot_answers_and_saves_faq_sources(self, mocked):
        response = self.client.post('/api/ai/chat/', {'message': 'How do I reset my password?'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['message']['source_faqs'][0]['id'], self.faq.id)
        session = ChatSession.objects.get(pk=response.data['session_id'])
        self.assertEqual(session.messages.count(), 2)

    @patch('ai_services.chat_views.generate_chat_answer', return_value='Hello')
    def test_chat_history_is_private(self, mocked):
        session = ChatSession.objects.create(user=self.other, title='Private')
        response = self.client.get(f'/api/ai/chat/sessions/{session.pk}/')
        self.assertEqual(response.status_code, 404)

    @patch('ai_services.chat_views.generate_chat_answer', return_value='Hello')
    def test_user_can_continue_existing_session(self, mocked):
        session = ChatSession.objects.create(user=self.user, title='Existing')
        response = self.client.post('/api/ai/chat/', {'message': 'Thanks', 'session_id': session.id}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatMessage.objects.filter(session=session).count(), 2)

    def test_message_is_required(self):
        response = self.client.post('/api/ai/chat/', {}, format='json')
        self.assertEqual(response.status_code, 400)
