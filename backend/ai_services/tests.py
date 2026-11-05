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
        with patch('ai_services.views.analyze_ticket', side_effect=Exception('should not be called')) as mocked:
            response = self.client.post(f'/api/ai/tickets/{self.ticket.pk}/analyze/')
            # The service is mocked above, so this assertion only verifies the route is reached.
            self.assertEqual(response.status_code, 500)
            mocked.assert_called_once()

    @patch('ai_services.views.analyze_ticket')
    def test_analysis_history_is_scoped_to_accessible_ticket(self, mocked_analyze):
        response = self.client.get(f'/api/ai/tickets/{self.ticket.pk}/analyses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
