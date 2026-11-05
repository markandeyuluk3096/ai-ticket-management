from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from categories.models import Category
from conversations.models import Message
from notifications.models import Notification
from tickets.models import Ticket

User = get_user_model()


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notify_user', password='StrongPass123!')
        self.other = User.objects.create_user(username='notify_other', password='StrongPass123!')
        self.notification = Notification.objects.create(recipient=self.user, title='Ticket update', message='Your ticket changed.')
        Notification.objects.create(recipient=self.other, title='Private', message='Other user notification.')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.user).access_token}')

    def test_user_only_sees_own_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_user_can_mark_own_notification_read(self):
        response = self.client.patch(f'/api/notifications/{self.notification.pk}/read/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_user_cannot_mark_another_users_notification_read(self):
        other_notification = Notification.objects.get(recipient=self.other)
        response = self.client.patch(f'/api/notifications/{other_notification.pk}/read/', {}, format='json')
        self.assertEqual(response.status_code, 404)


class AutomaticNotificationTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='ticket_customer', password='StrongPass123!', role='customer')
        self.agent = User.objects.create_user(username='ticket_agent', password='StrongPass123!', role='agent')
        self.category = Category.objects.create(name='Technical', code='TECH')

    def create_ticket(self):
        return Ticket.objects.create(
            ticket_number='TECH-2026-0001',
            customer=self.customer,
            category=self.category,
            subject='Cannot log in',
            description='Login is failing.',
        )

    def test_ticket_creation_notifies_customer(self):
        ticket = self.create_ticket()
        notification = Notification.objects.get(recipient=self.customer, title='Ticket created')
        self.assertIn(ticket.ticket_number, notification.message)

    def test_assignment_notifies_agent_and_customer(self):
        ticket = self.create_ticket()
        ticket.assigned_agent = self.agent
        ticket.save(update_fields=['assigned_agent'])

        self.assertTrue(Notification.objects.filter(recipient=self.agent, title='Ticket assigned to you').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.customer, title='Ticket assignment updated').exists())

    def test_status_change_notifies_customer(self):
        ticket = self.create_ticket()
        ticket.status = Ticket.Status.IN_PROGRESS
        ticket.save(update_fields=['status'])

        notification = Notification.objects.get(recipient=self.customer, title='Ticket status updated')
        self.assertIn('In Progress', notification.message)

    def test_new_customer_message_notifies_assigned_agent(self):
        ticket = self.create_ticket()
        ticket.assigned_agent = self.agent
        ticket.save(update_fields=['assigned_agent'])

        Message.objects.create(ticket=ticket, sender=self.customer, body='I can provide more details.')

        notification = Notification.objects.get(recipient=self.agent, title='New ticket reply')
        self.assertIn('I can provide more details.', notification.message)

    def test_agent_message_notifies_customer(self):
        ticket = self.create_ticket()
        ticket.assigned_agent = self.agent
        ticket.save(update_fields=['assigned_agent'])

        Message.objects.create(ticket=ticket, sender=self.agent, body='We are investigating.')

        notification = Notification.objects.filter(recipient=self.customer, title='New ticket reply').latest('created_at')
        self.assertIn('We are investigating.', notification.message)
