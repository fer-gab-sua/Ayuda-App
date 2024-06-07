from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Titular(models.Model):
    cbu_validator = RegexValidator(
        regex=r'^\d{22}$',
        message="El CBU debe tener exactamente 22 dígitos numéricos."
    )
    dni_validator = RegexValidator(
        regex=r'^\d+$',
        message="El DNI debe contener solo números."
    )

    titular_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100)
    address_detail = models.CharField(max_length=100, blank=True, null=True)
    dni = models.CharField(max_length=100, validators=[dni_validator])
    cbu = models.CharField(
        max_length=22,
        validators=[cbu_validator],
        unique=True,
        help_text="Ingrese el CBU de 22 dígitos."
    )
    titular_date = models.DateField("date published")
    user_upload = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Adherente(models.Model):
    adherente_id = models.AutoField(primary_key=True)
    titular = models.ForeignKey(Titular, on_delete=models.PROTECT, related_name='adherentes')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100)
    address_detail = models.CharField(max_length=100, blank=True, null=True)
    adherente_date = models.DateField("date published")
    adherente_date_down = models.DateField("date down", blank=True, null=True)
    user_upload = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

