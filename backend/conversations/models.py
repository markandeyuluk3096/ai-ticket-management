from django.conf import settings
from django.db import models
from tickets.models import Ticket


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ticket_messages')
    body = models.TextField(blank=True)
    attachment = models.FileField(upload_to='ticket_attachments/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message on {self.ticket.ticket_number} by {self.sender}'
