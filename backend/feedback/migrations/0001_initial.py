import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('tickets', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='TicketFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ticket_feedback', to=settings.AUTH_USER_MODEL)),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='tickets.ticket')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
