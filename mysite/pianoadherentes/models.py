from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Sucursales(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.descripcion

class DatosUser(models.Model):
    legajo = models.IntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    sucursal = models.ForeignKey(Sucursales, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self) -> str:
        return self.user.username


class Plan(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.descripcion

class Titular(models.Model):
    cbu_validator = RegexValidator(
        regex=r'^\d{22}$',
        message="El CBU debe tener exactamente 22 dígitos numéricos."
    )
    dni_validator = RegexValidator(
        regex=r'^\d+$',
        message="El DNI debe contener solo números."
    )

    titular_id = models.AutoField(primary_key=True) #
    name = models.CharField(max_length=100) #
    last_name = models.CharField(max_length=100) #
    document_type = models.CharField(max_length=10) #
    document = models.CharField(max_length=100, validators=[dni_validator]) 
    birthdate = models.DateField(blank=True, null=True) 
    sex = models.CharField(max_length=10)
    street_address = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    floor = models.CharField(max_length=10, blank=True, null=True)
    between_street =  models.CharField(max_length=100, blank=True, null=True)
    province =  models.CharField(max_length=100)
    city =  models.CharField(max_length=30)
    postal_code =  models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cbu = models.CharField(
        max_length=22,
        validators=[cbu_validator],
        unique=True,
        help_text="Ingrese el CBU de 22 dígitos."
    )
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(blank=True, null=True)
    user_upload = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    migrate = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

    class Meta:
        permissions = [
            ("can_view_stats", "Can view statistics"),
            ("can_view_stats_controller", "Can view statistics controller"),
        ]


class Adherente(models.Model):
    dni_validator = RegexValidator(
        regex=r'^\d+$',
        message="El DNI debe contener solo números."
    )

    adherente_id = models.AutoField(primary_key=True)
    titular = models.ForeignKey(Titular, on_delete=models.PROTECT, related_name='adherentes')
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=10)
    document = models.CharField(max_length=100, validators=[dni_validator])
    birthdate = models.DateField(blank=True, null=True) 
    sex = models.CharField(max_length=10)
    street_address = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    floor = models.CharField(max_length=10, blank=True, null=True)
    between_street =  models.CharField(max_length=100, blank=True, null=True)
    province =  models.CharField(max_length=100)
    city =  models.CharField(max_length=30)
    postal_code =  models.CharField(max_length=20)
    plan = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(blank=True, null=True)
    user_upload = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    migrate = models.BooleanField(default=False)

    
    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            ("can_view_stats", "Can view statistics"),
        ]

class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    adherente = models.ForeignKey(Adherente,on_delete=models.PROTECT, related_name='adherentes')
    movimiento = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    historia = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_view_stats_log", "Can view statistics log"),
        ]
