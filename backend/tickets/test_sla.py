from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from categories.models import Category
from notifications.models import Notification
from tickets.models import Ticket

User = get_user_model()


class TicketSLATests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='sla_customer', password='StrongPass123!')
        self.agent = User.objects.create_user(username='sla_agent', password='StrongPass123!', role='agent')
        self.category = Category.objects.create(name='SLA Technical', code='SLATECH')

    def make_ticket(self, priority='medium', status=Ticket.Status.OPEN, assigned_agent=None):
        return Ticket.objects.create(
            ticket_number=f'SLATECH-{timezone.localdate().year}-0001',
            customer=self.customer, category=self.category, subject='SLA test ticket',
            description='Testing SLA tracking.', priority=priority, status=status,
            assigned_agent=assigned_agent,
        )

    def test_deadline_is_set_based_on_priority(self):
        before = timezone.now()
        ticket = self.make_ticket(priority=Ticket.Priority.URGENT)
        after = timezone.now()
        self.assertGreaterEqual(ticket.sla_due_at, before + timedelta(hours=4))
        self.assertLessEqual(ticket.sla_due_at, after + timedelta(hours=4))

    def test_priority_change_recalculates_deadline(self):
        ticket = self.make_ticket(priority=Ticket.Priority.LOW)
        ticket.priority = Ticket.Priority.HIGH
        ticket.save(update_fields=['priority'])
        self.assertGreater(ticket.sla_due_at, timezone.now())
        self.assertLess(ticket.sla_due_at, timezone.now() + timedelta(hours=9))

    def test_overdue_command_marks_ticket_and_notifies_agent(self):
        ticket = self.make_ticket(assigned_agent=self.agent)
        Ticket.objects.filter(pk=ticket.pk).update(sla_due_at=timezone.now() - timedelta(minutes=1))
        call_command('check_sla')
        ticket.refresh_from_db()
        self.assertIsNotNone(ticket.sla_breached_at)
        self.assertTrue(Notification.objects.filter(recipient=self.agent, title='Ticket SLA breached').exists())

    def test_resolved_ticket_is_not_marked_overdue(self):
        ticket = self.make_ticket(status=Ticket.Status.RESOLVED)
        Ticket.objects.filter(pk=ticket.pk).update(sla_due_at=timezone.now() - timedelta(minutes=1))
        call_command('check_sla')
        ticket.refresh_from_db()
        self.assertIsNone(ticket.sla_breached_at)

    def test_overdue_property_ignores_resolved_tickets(self):
        ticket = self.make_ticket()
        Ticket.objects.filter(pk=ticket.pk).update(sla_due_at=timezone.now() - timedelta(minutes=1))
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_sla_overdue)
        ticket.status = Ticket.Status.CLOSED
        ticket.save(update_fields=['status'])
        self.assertFalse(ticket.is_sla_overdue)
