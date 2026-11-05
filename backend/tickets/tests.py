from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from categories.models import Category
from .models import Ticket

User = get_user_model()


class TicketAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='ticket_customer', password='StrongPass123!')
        self.other_customer = User.objects.create_user(username='other_customer', password='StrongPass123!')
        self.agent = User.objects.create_user(username='ticket_agent', password='StrongPass123!', role='agent')
        self.category = Category.objects.create(name='Technical', code='TECH')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.customer).access_token}')

    def test_customer_can_create_ticket_and_receives_category_number(self):
        response = self.client.post('/api/tickets/', {
            'subject': 'Cannot log in',
            'description': 'Login page returns an error.',
            'category_id': self.category.pk,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['ticket_number'], f'TECH-{timezone.localdate().year}-0001')
        self.assertEqual(response.data['customer'], self.customer.pk)

    def test_customer_only_sees_own_tickets(self):
        Ticket.objects.create(ticket_number='TECH-2026-0001', customer=self.other_customer, category=self.category, subject='Private', description='Private ticket')
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], [])

    def test_customer_cannot_change_ticket_status(self):
        ticket = Ticket.objects.create(ticket_number='TECH-2026-0001', customer=self.customer, category=self.category, subject='Help', description='Need help')
        response = self.client.patch(f'/api/tickets/{ticket.pk}/', {'status': 'closed'}, format='json')
        self.assertEqual(response.status_code, 403)
