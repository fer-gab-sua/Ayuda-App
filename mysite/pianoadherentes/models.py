from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone

class Sucursales(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.descripcion

class DatosUser(models.Model):
    legajo = models.IntegerField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    plan = models.CharField(max_length=20, blank=True, null=True, default="Basico")
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
            ("can_view_stats_controllerAdmin", "Can view statistics controller Admin"),
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
    legajo = models.IntegerField(blank=True)
    sucursal = models.CharField(max_length=50)

    
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


class Movimiento(models.Model):
    titular = models.ForeignKey(Titular, on_delete=models.PROTECT)
    adherente = models.ForeignKey(Adherente, on_delete=models.PROTECT, blank=True, null=True)
    tipo_persona = models.CharField(max_length=10, choices=[('Titular', 'Titular'), ('Adherente', 'Adherente')])
    movimiento = models.CharField(max_length=20, choices=[
        ('Alta', 'Alta'), ('Modificacion', 'Modificacion'),
        ('Baja', 'Baja'), ('Reactivacion', 'Reactivacion'),
    ])
    nombre = models.CharField(max_length=201)
    documento = models.CharField(max_length=100)
    cbu = models.CharField(max_length=22)
    plan_anterior = models.CharField(max_length=20, blank=True)
    plan_nuevo = models.CharField(max_length=20, blank=True)
    activo_anterior = models.BooleanField(null=True)
    activo_nuevo = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    usuario = models.CharField(max_length=150)
    legajo = models.IntegerField(blank=True, null=True)
    sucursal = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    venta_plus = models.BooleanField(default=False, db_index=True)
    salida_plus = models.BooleanField(default=False)
    reingreso_plus = models.BooleanField(default=False)
    ingreso_plus_anterior = models.DateTimeField(blank=True, null=True)
    salida_plus_anterior = models.DateTimeField(blank=True, null=True)
    usuario_salida_plus = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['created', 'pk']
        verbose_name = 'movimiento'
        verbose_name_plural = 'movimientos'
        permissions = [
            ('can_view_movimientos', 'Puede ver movimientos y ventas Plus de todos los usuarios'),
        ]
        indexes = [
            models.Index(fields=['titular', 'adherente', 'created'], name='mov_persona_fecha_idx'),
        ]

    def __str__(self):
        return f'{self.movimiento} - {self.tipo_persona} {self.nombre}'

    @property
    def dias_fuera_plus(self):
        if self.reingreso_plus and self.salida_plus_anterior is not None:
            return (self.created - self.salida_plus_anterior).total_seconds() / 86400
        return None
