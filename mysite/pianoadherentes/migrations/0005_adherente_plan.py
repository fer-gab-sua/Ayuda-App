# Generated by Django 4.2.13 on 2024-09-13 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pianoadherentes', '0004_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='adherente',
            name='plan',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='pianoadherentes.plan'),
            preserve_default=False,
        ),
    ]