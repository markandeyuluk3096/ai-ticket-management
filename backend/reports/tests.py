from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from categories.models import Category
from tickets.models import Ticket
from feedback.models import TicketFeedback

User = get_user_model()


class FeedbackAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='feedback_customer', password='StrongPass123!')
        self.other = User.objects.create_user(username='feedback_other', password='StrongPass123!')
        self.category = Category.objects.create(name='Support', code='SUP')
        self.ticket = Ticket.objects.create(ticket_number='SUP-2026-0001', customer=self.customer, category=self.category, subject='Help', description='Need help', status='resolved')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.customer).access_token}')

    def test_customer_can_submit_feedback_for_resolved_ticket(self):
        response = self.client.post(f'/api/feedback/tickets/{self.ticket.pk}/', {'rating': 5, 'comment': 'Great support'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['customer'], self.customer.pk)

    def test_customer_cannot_submit_feedback_for_another_ticket(self):
        other_ticket = Ticket.objects.create(ticket_number='SUP-2026-0002', customer=self.other, category=self.category, subject='Other', description='Private', status='closed')
        response = self.client.post(f'/api/feedback/tickets/{other_ticket.pk}/', {'rating': 4}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_feedback_is_limited_to_one_per_ticket(self):
        TicketFeedback.objects.create(ticket=self.ticket, customer=self.customer, rating=4)
        response = self.client.post(f'/api/feedback/tickets/{self.ticket.pk}/', {'rating': 5}, format='json')
        self.assertEqual(response.status_code, 400)


class AdminReportAPITests(APITestCase):
    def test_only_admin_can_access_dashboard_report(self):
        customer = User.objects.create_user(username='report_customer', password='StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(customer).access_token}')
        response = self.client.get('/api/reports/dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_dashboard_report(self):
        admin = User.objects.create_user(username='report_admin', password='StrongPass123!', role='admin', is_staff=True)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(admin).access_token}')
        response = self.client.get('/api/reports/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_tickets', response.data)
