from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from categories.models import Category
from .models import Ticket
from .attachments import TicketAttachment

User = get_user_model()


class TicketAutomationAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='automation_customer', password='StrongPass123!')
        self.other = User.objects.create_user(username='automation_other', password='StrongPass123!')
        self.category = Category.objects.create(name='General', code='GEN')
        self.ticket = Ticket.objects.create(ticket_number='GEN-2026-0001', customer=self.customer, category=self.category, subject='Cannot access account', description='I cannot sign in to my account.')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.customer).access_token}')

    def test_similar_ticket_endpoint_finds_candidate(self):
        Ticket.objects.create(ticket_number='GEN-2026-0002', customer=self.customer, category=self.category, subject='Cannot access my account', description='I cannot sign in to my account.')
        response = self.client.get(f'/api/tickets/{self.ticket.pk}/similar/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['possible_duplicates']), 1)

    def test_similar_ticket_endpoint_does_not_expose_other_customer_tickets(self):
        Ticket.objects.create(ticket_number='GEN-2026-0002', customer=self.other, category=self.category, subject='Cannot access account', description='I cannot sign in to my account.')
        response = self.client.get(f'/api/tickets/{self.ticket.pk}/similar/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['possible_duplicates'], [])

    def test_customer_can_upload_pdf_attachment(self):
        upload = SimpleUploadedFile('error.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        response = self.client.post(f'/api/tickets/{self.ticket.pk}/attachments/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(TicketAttachment.objects.count(), 1)

    def test_customer_cannot_upload_executable(self):
        upload = SimpleUploadedFile('malware.exe', b'bad', content_type='application/octet-stream')
        response = self.client.post(f'/api/tickets/{self.ticket.pk}/attachments/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 400)
