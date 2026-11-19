from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from categories.models import Category
from .models import Ticket, TicketAttachment

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

    def test_customer_cannot_upload_non_pdf_renamed_as_pdf(self):
        upload = SimpleUploadedFile('fake.pdf', b'this is not a PDF', content_type='application/pdf')
        response = self.client.post(f'/api/tickets/{self.ticket.pk}/attachments/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_customer_cannot_upload_invalid_docx(self):
        upload = SimpleUploadedFile('fake.docx', b'not a zip document', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response = self.client.post(f'/api/tickets/{self.ticket.pk}/attachments/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 400)


class TicketStaffPermissionAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='staff_test_customer', password='StrongPass123!')
        self.agent = User.objects.create_user(username='staff_test_agent', password='StrongPass123!', role='agent')
        self.other_agent = User.objects.create_user(username='staff_test_other_agent', password='StrongPass123!', role='agent')
        self.admin = User.objects.create_user(username='staff_test_admin', password='StrongPass123!', role='admin')
        self.category = Category.objects.create(name='Staff Test', code='STF')
        self.ticket = Ticket.objects.create(
            ticket_number=f'STF-{timezone.localdate().year}-0001',
            customer=self.customer,
            category=self.category,
            subject='Staff workflow test',
            description='Test agent access and assignment permissions.',
            assigned_agent=self.agent,
        )

    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')

    def test_assigned_agent_can_update_ticket_status_and_priority(self):
        self.authenticate(self.agent)
        response = self.client.patch(
            f'/api/tickets/{self.ticket.pk}/',
            {'status': 'in_progress', 'priority': 'high'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'in_progress')
        self.assertEqual(self.ticket.priority, 'high')

    def test_assigned_agent_cannot_reassign_ticket(self):
        self.authenticate(self.agent)
        response = self.client.patch(
            f'/api/tickets/{self.ticket.pk}/',
            {'assigned_agent': self.other_agent.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_agent_id, self.agent.pk)

    def test_unassigned_agent_cannot_read_or_update_ticket(self):
        self.authenticate(self.other_agent)
        response = self.client.get(f'/api/tickets/{self.ticket.pk}/')
        self.assertEqual(response.status_code, 403)

    def test_agent_queue_contains_only_assigned_tickets(self):
        Ticket.objects.create(
            ticket_number=f'STF-{timezone.localdate().year}-0002',
            customer=self.customer,
            category=self.category,
            subject='Unassigned test ticket',
            description='This ticket is not assigned to this agent.',
        )
        self.authenticate(self.agent)
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['results']], [self.ticket.pk])

    def test_administrator_can_assign_ticket_to_agent(self):
        self.authenticate(self.admin)
        response = self.client.patch(
            f'/api/tickets/{self.ticket.pk}/',
            {'assigned_agent': self.other_agent.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_agent_id, self.other_agent.pk)
