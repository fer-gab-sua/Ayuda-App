from django.db import transaction
from django.utils import timezone

from .models import Adherente, DatosUser, Movimiento


def es_plus(plan):
    return (plan or '').strip().casefold() == 'plus'


@transaction.atomic
def guardar_con_movimiento(persona, usuario):
    anterior = None
    if not persona._state.adding:
        anterior = type(persona).objects.select_for_update().get(pk=persona.pk)

    fecha = timezone.now()
    if anterior is None:
        operacion = 'Alta'
    elif anterior.is_active and not persona.is_active:
        operacion = 'Baja'
        persona.deleted = fecha
    elif not anterior.is_active and persona.is_active:
        operacion = 'Reactivacion'
        persona.deleted = None
    else:
        operacion = 'Modificacion'

    adherente = persona if isinstance(persona, Adherente) else None
    titular = persona.titular if adherente is not None else persona
    historial = Movimiento.objects.none()
    if anterior is not None:
        historial = Movimiento.objects.filter(adherente=adherente) if adherente is not None else Movimiento.objects.filter(
            titular=titular, adherente__isnull=True,
        )
    plus_activo_anterior = anterior is not None and anterior.is_active and es_plus(anterior.plan)
    plus_activo_nuevo = persona.is_active and es_plus(persona.plan)
    venta_plus = plus_activo_nuevo and not plus_activo_anterior
    ultima_venta = historial.filter(venta_plus=True).order_by('-created', '-pk').first()
    ultima_salida = historial.filter(salida_plus=True).order_by('-created', '-pk').first()
    plus_previo_sin_fecha = False
    if venta_plus and anterior is not None and ultima_venta is None and ultima_salida is None:
        primer_movimiento = historial.first()
        plus_previo_sin_fecha = es_plus(primer_movimiento.plan_anterior if primer_movimiento else anterior.plan)
    reingreso = venta_plus and (
        ultima_venta is not None or ultima_salida is not None
        or plus_previo_sin_fecha
    )
    fecha_ingreso = ultima_venta.created if ultima_venta else None
    fecha_salida = ultima_salida.created if ultima_salida else None
    usuario_salida = ultima_salida.usuario if ultima_salida else ''
    observaciones = []
    if reingreso:
        observaciones.append('Reingreso a Plus: ya tenia una contratacion anterior.')
        if fecha_ingreso:
            observaciones.append(f'Ingreso anterior: {fecha_ingreso:%d/%m/%Y %H:%M:%S}.')
        else:
            observaciones.append('Fecha de ingreso anterior no disponible (anterior al historial).')
        if fecha_salida is None and anterior is not None and not anterior.is_active:
            fecha_salida = anterior.deleted
        if fecha_salida:
            observaciones.append(f'Baja o salida de Plus: {fecha_salida:%d/%m/%Y %H:%M:%S}.')
            if usuario_salida:
                observaciones.append(f'Usuario de la baja o salida: {usuario_salida}.')
            dias = (fecha - fecha_salida).total_seconds() / 86400
            observaciones.append(f'Tiempo fuera de Plus: {dias:.6f} dias.')
        else:
            observaciones.append('Fecha de baja o salida anterior no disponible.')
        observaciones.append(f'Nueva activacion: {fecha:%d/%m/%Y %H:%M:%S}. Revisar antes de liquidar.')
    if anterior is not None and es_plus(anterior.plan) and not historial.exists():
        observaciones.append('Plan Plus preexistente: sin historial previo verificable.')

    datos_usuario = DatosUser.objects.select_related('sucursal').filter(user=usuario).first()
    if datos_usuario is None:
        observaciones.append('Usuario sin legajo/sucursal configurados al momento de la operacion.')
    elif datos_usuario.sucursal is None:
        observaciones.append('Usuario sin sucursal configurada al momento de la operacion.')

    persona.save()
    return Movimiento.objects.create(
        titular=titular, adherente=adherente,
        tipo_persona='Adherente' if adherente is not None else 'Titular',
        movimiento=operacion, nombre=f'{persona.name} {persona.last_name}',
        documento=persona.document, cbu=titular.cbu,
        plan_anterior=(anterior.plan or '') if anterior else '',
        plan_nuevo=persona.plan or '',
        activo_anterior=anterior.is_active if anterior else None,
        activo_nuevo=persona.is_active, user=usuario, usuario=usuario.username,
        legajo=datos_usuario.legajo if datos_usuario else None,
        sucursal=datos_usuario.sucursal.descripcion if datos_usuario and datos_usuario.sucursal else '',
        created=fecha, venta_plus=venta_plus,
        salida_plus=plus_activo_anterior and not plus_activo_nuevo,
        reingreso_plus=reingreso,
        ingreso_plus_anterior=fecha_ingreso if reingreso else None,
        salida_plus_anterior=fecha_salida if reingreso else None,
        usuario_salida_plus=usuario_salida if reingreso else '',
        observaciones=' '.join(observaciones),
    )
