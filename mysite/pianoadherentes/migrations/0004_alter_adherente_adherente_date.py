# Generated by Django 4.2.13 on 2024-06-11 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pianoadherentes', '0003_adherente_dni_alter_titular_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adherente',
            name='adherente_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
