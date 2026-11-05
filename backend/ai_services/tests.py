from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from categories.models import Category
from tickets.models import Ticket
from .models import TicketAIAnalysis

User = get_user_model()


class TicketAIAnalysisAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='ai_customer', password='StrongPass123!')
        self.other = User.objects.create_user(username='ai_other', password='StrongPass123!')
        self.category = Category.objects.create(name='Technical', code='TECH')
        self.ticket = Ticket.objects.create(ticket_number='TECH-2026-0001', customer=self.customer, category=self.category, subject='Cannot log in', description='The login page displays an error.')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.customer).access_token}')
        self.result = {
            'category': 'Technical', 'priority': 'high', 'sentiment': 'negative',
            'summary': 'Customer cannot log in.', 'suggested_response': 'Please share the error details.',
        }

    @patch('ai_services.views.analyze_ticket')
    def test_customer_can_request_analysis_for_own_ticket(self, mocked_analyze):
        mocked_analyze.return_value = self.result
        response = self.client.post(f'/api/ai/tickets/{self.ticket.pk}/analyze/')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['result']['priority'], 'high')
        self.assertEqual(TicketAIAnalysis.objects.count(), 1)

    @patch('ai_services.views.analyze_ticket')
    def test_customer_cannot_analyze_another_customers_ticket(self, mocked_analyze):
        other_ticket = Ticket.objects.create(ticket_number='TECH-2026-0002', customer=self.other, category=self.category, subject='Private', description='Private')
        response = self.client.post(f'/api/ai/tickets/{other_ticket.pk}/analyze/')
        self.assertEqual(response.status_code, 403)
        mocked_analyze.assert_not_called()

    @override_settings(OPENAI_API_KEY='')
    def test_missing_api_key_returns_service_unavailable(self):
        response = self.client.post(f'/api/ai/tickets/{self.ticket.pk}/analyze/')
        self.assertEqual(response.status_code, 503)
        self.assertIn('OPENAI_API_KEY', response.data['detail'])

    @patch('ai_services.views.analyze_ticket')
    def test_analysis_history_is_scoped_to_accessible_ticket(self, mocked_analyze):
        response = self.client.get(f'/api/ai/tickets/{self.ticket.pk}/analyses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


from .chat_views import ChatMessageAPIView
from .models import ChatSession, ChatMessage
from faqs.models import FAQ


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

    def test_chat_history_is_private(self):
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
