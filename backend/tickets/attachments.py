import os
import uuid
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import models
from .models import Ticket


def ticket_attachment_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'ticket_attachments/{instance.ticket_id}/{uuid.uuid4().hex}{extension}'


def validate_attachment(file):
    allowed = {'.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'}
    extension = Path(file.name).suffix.lower()
    if extension not in allowed:
        raise ValidationError('Unsupported file type. Allowed: PDF, PNG, JPG, TXT, DOCX.')
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('Attachment size must not exceed 5 MB.')


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='ticket_attachments')
    file = models.FileField(upload_to=ticket_attachment_path, validators=[validate_attachment])
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_name
