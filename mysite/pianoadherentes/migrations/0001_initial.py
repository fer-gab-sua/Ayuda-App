# Generated by Django 4.2.13 on 2024-06-06 00:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Titular',
            fields=[
                ('titular_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(max_length=100)),
                ('address_detail', models.CharField(blank=True, max_length=100, null=True)),
                ('dni', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(message='El DNI debe contener solo números.', regex='^\\d+$')])),
                ('cbu', models.CharField(help_text='Ingrese el CBU de 22 dígitos.', max_length=22, unique=True, validators=[django.core.validators.RegexValidator(message='El CBU debe tener exactamente 22 dígitos numéricos.', regex='^\\d{22}$')])),
                ('titular_date', models.DateField(verbose_name='date published')),
                ('is_active', models.BooleanField(default=True)),
                ('user_upload', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Adherente',
            fields=[
                ('adherente_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(max_length=100)),
                ('address_detail', models.CharField(blank=True, max_length=100, null=True)),
                ('adherente_date', models.DateField(verbose_name='date published')),
                ('adherente_date_down', models.DateField(blank=True, null=True, verbose_name='date down')),
                ('is_active', models.BooleanField(default=True)),
                ('titular', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='adherentes', to='pianoadherentes.titular')),
                ('user_upload', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
