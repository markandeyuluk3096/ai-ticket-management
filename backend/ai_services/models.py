from django.conf import settings
from django.db import models
from tickets.models import Ticket


class TicketAIAnalysis(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ai_analyses')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requested_ai_analyses')
    provider = models.CharField(max_length=40, default='openai')
    model_name = models.CharField(max_length=80)
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'AI analysis for {self.ticket.ticket_number} ({self.created_at:%Y-%m-%d %H:%M})'
