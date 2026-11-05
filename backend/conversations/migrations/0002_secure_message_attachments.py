import conversations.models
import tickets.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('conversations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='attachment',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=conversations.models.message_attachment_path,
                validators=[tickets.models.validate_attachment],
            ),
        ),
    ]
