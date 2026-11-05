from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from conversations.models import Message
from tickets.models import Ticket
from .models import Notification


def ticket_link(ticket):
    return f'/api/tickets/{ticket.pk}/'


@receiver(pre_save, sender=Ticket, dispatch_uid='notifications_capture_ticket_changes')
def capture_ticket_changes(sender, instance, **kwargs):
    instance._notification_previous_values = None
    if instance.pk:
        instance._notification_previous_values = (
            Ticket.objects.filter(pk=instance.pk)
            .values('status', 'assigned_agent_id')
            .first()
        )


@receiver(post_save, sender=Ticket, dispatch_uid='notifications_ticket_events')
def notify_ticket_events(sender, instance, created, **kwargs):
    link = ticket_link(instance)

    if created:
        Notification.objects.create(
            recipient=instance.customer,
            title='Ticket created',
            message=f'Your ticket {instance.ticket_number} has been created.',
            link=link,
        )
        if instance.assigned_agent_id:
            Notification.objects.create(
                recipient=instance.assigned_agent,
                title='New ticket assigned',
                message=f'Ticket {instance.ticket_number} has been assigned to you.',
                link=link,
            )
        return

    previous = getattr(instance, '_notification_previous_values', None)
    if not previous:
        return

    if previous['status'] != instance.status:
        Notification.objects.create(
            recipient=instance.customer,
            title='Ticket status updated',
            message=f'Ticket {instance.ticket_number} is now {instance.get_status_display()}.',
            link=link,
        )

    if previous['assigned_agent_id'] != instance.assigned_agent_id:
        if instance.assigned_agent_id:
            Notification.objects.create(
                recipient=instance.assigned_agent,
                title='Ticket assigned to you',
                message=f'Ticket {instance.ticket_number} has been assigned to you.',
                link=link,
            )
            customer_message = f'Ticket {instance.ticket_number} has been assigned to a support agent.'
        else:
            customer_message = f'Ticket {instance.ticket_number} is currently unassigned.'

        Notification.objects.create(
            recipient=instance.customer,
            title='Ticket assignment updated',
            message=customer_message,
            link=link,
        )


@receiver(post_save, sender=Message, dispatch_uid='notifications_message_events')
def notify_message_recipients(sender, instance, created, **kwargs):
    if not created:
        return

    ticket = instance.ticket
    recipients = []
    if ticket.customer_id != instance.sender_id:
        recipients.append(ticket.customer)
    if ticket.assigned_agent_id and ticket.assigned_agent_id != instance.sender_id:
        recipients.append(ticket.assigned_agent)

    message_text = instance.body.strip()
    if not message_text:
        message_text = 'A new attachment was added to the conversation.'

    for recipient in recipients:
        Notification.objects.create(
            recipient=recipient,
            title='New ticket reply',
            message=f'{instance.sender.username} replied on ticket {ticket.ticket_number}: {message_text[:180]}',
            link=f'/api/tickets/{ticket.pk}/',
        )
