import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('categories', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_number', models.CharField(editable=False, max_length=32, unique=True)),
                ('subject', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('waiting', 'Waiting for Customer'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('assigned_agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='categories.category')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='customer_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(model_name='ticket', index=models.Index(fields=['status', 'priority'], name='tickets_tic_status_3d4f6a_idx')),
        migrations.AddIndex(model_name='ticket', index=models.Index(fields=['customer', 'created_at'], name='tickets_tic_custome_9a6c51_idx')),
        migrations.AddIndex(model_name='ticket', index=models.Index(fields=['assigned_agent', 'status'], name='tickets_tic_assigne_1b6f8c_idx')),
    ]
