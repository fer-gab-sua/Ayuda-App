# Generated by Django 4.2.13 on 2024-06-15 01:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pianoadherentes', '0004_alter_adherente_adherente_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adherente',
            options={'permissions': [('can_view_stats', 'Can view statistics')]},
        ),
        migrations.AlterModelOptions(
            name='titular',
            options={'permissions': [('can_view_stats', 'Can view statistics')]},
        ),
    ]
