# Generated by Django 4.2.13 on 2024-11-01 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pianoadherentes', '0019_alter_contratos_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratos',
            name='link_firma',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]