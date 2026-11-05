from django.db import migrations


def promote_existing_superusers(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(is_superuser=True).exclude(role='admin').update(role='admin')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_email'),
    ]

    operations = [
        migrations.RunPython(promote_existing_superusers, migrations.RunPython.noop),
    ]
