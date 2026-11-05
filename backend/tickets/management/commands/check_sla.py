from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from notifications.models import Notification
from tickets.models import Ticket


class Command(BaseCommand):
    help = 'Mark active tickets whose SLA deadline has passed and notify the responsible team.'

    def handle(self, *args, **options):
        now = timezone.now()
        User = get_user_model()
        breached_count = 0
        overdue_tickets = Ticket.objects.filter(sla_due_at__lte=now, sla_breached_at__isnull=True).exclude(
            status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
        )
        for ticket in overdue_tickets.iterator():
            with transaction.atomic():
                locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
                if locked.sla_breached_at is not None or locked.status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
                    continue
                locked.sla_breached_at = now
                locked.save(update_fields=['sla_breached_at'])
                recipients = [locked.assigned_agent] if locked.assigned_agent_id else list(User.objects.filter(role='admin', is_active=True))
                for recipient in recipients:
                    Notification.objects.create(
                        recipient=recipient,
                        title='Ticket SLA breached',
                        message=f'Ticket {locked.ticket_number} passed its SLA deadline.',
                        link=f'/api/tickets/{locked.pk}/',
                    )
                breached_count += 1
        self.stdout.write(self.style.SUCCESS(f'Processed {breached_count} overdue ticket(s).'))
