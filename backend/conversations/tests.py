from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from categories.models import Category
from tickets.models import Ticket

User = get_user_model()


class ConversationAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='message_customer', password='StrongPass123!')
        self.other = User.objects.create_user(username='message_other', password='StrongPass123!')
        self.category = Category.objects.create(name='Billing', code='BILL')
        self.ticket = Ticket.objects.create(ticket_number='BILL-2026-0001', customer=self.customer, category=self.category, subject='Invoice', description='Question about invoice')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.customer).access_token}')

    def test_customer_can_post_message_on_own_ticket(self):
        response = self.client.post(f'/api/tickets/{self.ticket.pk}/messages/', {'body': 'I need help with this invoice.'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['sender'], self.customer.pk)

    def test_customer_cannot_read_another_customers_messages(self):
        other_ticket = Ticket.objects.create(ticket_number='BILL-2026-0002', customer=self.other, category=self.category, subject='Other invoice', description='Private')
        response = self.client.get(f'/api/tickets/{other_ticket.pk}/messages/')
        self.assertEqual(response.status_code, 403)
