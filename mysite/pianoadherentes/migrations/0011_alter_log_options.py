# Generated by Django 4.2.13 on 2024-09-17 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pianoadherentes', '0010_alter_datosuser_sucursal'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'permissions': [('can_view_stats_log', 'Can view statistics log')]},
        ),
    ]
