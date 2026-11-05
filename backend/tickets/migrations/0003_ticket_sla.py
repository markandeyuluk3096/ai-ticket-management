from datetime import timedelta
from django.db import migrations, models


def populate_sla_deadlines(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    hours_by_priority = {'urgent': 4, 'high': 8, 'medium': 24, 'low': 72}
    for ticket in Ticket.objects.all().iterator():
        ticket.sla_due_at = ticket.created_at + timedelta(hours=hours_by_priority.get(ticket.priority, 24))
        ticket.save(update_fields=['sla_due_at'])


class Migration(migrations.Migration):
    dependencies = [('tickets', '0002_ticketattachment')]
    operations = [
        migrations.AddField(model_name='ticket', name='sla_due_at', field=models.DateTimeField(blank=True, editable=False, null=True)),
        migrations.AddField(model_name='ticket', name='sla_breached_at', field=models.DateTimeField(blank=True, editable=False, null=True)),
        migrations.AddIndex(model_name='ticket', index=models.Index(fields=['sla_due_at', 'status'], name='tkt_sla_due_status_idx')),
        migrations.RunPython(populate_sla_deadlines, migrations.RunPython.noop),
    ]
