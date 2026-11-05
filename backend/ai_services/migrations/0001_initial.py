import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('tickets', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='TicketAIAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(default='openai', max_length=40)),
                ('model_name', models.CharField(max_length=80)),
                ('result', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requested_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_ai_analyses', to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_analyses', to='tickets.ticket')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
