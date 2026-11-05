from datetime import timedelta
from pathlib import Path
import uuid
import zipfile

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        WAITING = 'waiting', 'Waiting for Customer'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    SLA_HOURS = {Priority.URGENT: 4, Priority.HIGH: 8, Priority.MEDIUM: 24, Priority.LOW: 72}

    ticket_number = models.CharField(max_length=32, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='customer_tickets')
    category = models.ForeignKey('categories.Category', on_delete=models.PROTECT, related_name='tickets')
    assigned_agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sla_due_at = models.DateTimeField(null=True, blank=True, editable=False)
    sla_breached_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority'], name='tkt_status_prio_idx'),
            models.Index(fields=['customer', 'created_at'], name='tkt_customer_date_idx'),
            models.Index(fields=['assigned_agent', 'status'], name='tkt_agent_status_idx'),
            models.Index(fields=['sla_due_at', 'status'], name='tkt_sla_due_status_idx'),
        ]

    @property
    def is_sla_overdue(self):
        return self.sla_due_at is not None and self.sla_due_at <= timezone.now() and self.status not in (self.Status.RESOLVED, self.Status.CLOSED)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        recalculate_sla = self.sla_due_at is None or self._state.adding
        if self.pk and not self._state.adding:
            previous_priority = Ticket.objects.filter(pk=self.pk).values_list('priority', flat=True).first()
            if previous_priority is not None and previous_priority != self.priority:
                recalculate_sla = True
        if recalculate_sla:
            self.sla_due_at = timezone.now() + timedelta(hours=self.SLA_HOURS[self.priority])
            self.sla_breached_at = None
            if update_fields is not None:
                kwargs['update_fields'] = set(update_fields) | {'sla_due_at', 'sla_breached_at'}
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_number or f'Ticket #{self.pk}'


def ticket_attachment_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'ticket_attachments/{instance.ticket_id}/{uuid.uuid4().hex}{extension}'


def validate_attachment(file):
    """Check both the filename extension and the actual file contents."""
    allowed = {'.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'}
    extension = Path(file.name).suffix.lower()
    if extension not in allowed:
        raise ValidationError('Unsupported file type. Allowed: PDF, PNG, JPG, TXT, DOCX.')
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('Attachment size must not exceed 5 MB.')
    try:
        file.seek(0)
        header = file.read(8)
        file.seek(0)
        if extension == '.pdf' and not header.startswith(b'%PDF-'):
            raise ValidationError('The uploaded file is not a valid PDF.')
        if extension == '.png' and header != b'\x89PNG\r\n\x1a\n':
            raise ValidationError('The uploaded file is not a valid PNG image.')
        if extension in {'.jpg', '.jpeg'} and not header.startswith(b'\xff\xd8\xff'):
            raise ValidationError('The uploaded file is not a valid JPEG image.')
        if extension == '.txt':
            content = file.read()
            if b'\x00' in content:
                raise ValidationError('Text attachments must be valid UTF-8 text.')
            try:
                content.decode('utf-8')
            except UnicodeDecodeError:
                raise ValidationError('Text attachments must be valid UTF-8 text.')
        if extension == '.docx':
            if not zipfile.is_zipfile(file):
                raise ValidationError('The uploaded file is not a valid DOCX document.')
            file.seek(0)
            with zipfile.ZipFile(file) as document:
                if 'word/document.xml' not in document.namelist():
                    raise ValidationError('The uploaded file is not a valid DOCX document.')
    finally:
        file.seek(0)


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ticket_attachments')
    file = models.FileField(upload_to=ticket_attachment_path, validators=[validate_attachment])
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_name
