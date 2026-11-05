import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import tickets.models


class Migration(migrations.Migration):
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('tickets', '0001_initial')]
    operations = [migrations.CreateModel(name='TicketAttachment', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('file', models.FileField(upload_to=tickets.models.ticket_attachment_path, validators=[tickets.models.validate_attachment])),
        ('original_name', models.CharField(max_length=255)),
        ('uploaded_at', models.DateTimeField(auto_now_add=True)),
        ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='tickets.ticket')),
        ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ticket_attachments', to=settings.AUTH_USER_MODEL)),
    ], options={'ordering': ['-uploaded_at']})]
