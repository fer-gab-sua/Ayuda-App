from django.contrib.auth.decorators import permission_required
from ..models import Titular , Adherente, Log, Sucursales
from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from zipfile import BadZipFile

@permission_required('pianoadherentes.can_view_stats', raise_exception=True)
def estadisticas(request):
    sucursales = Sucursales.objects.all()
    usuarios = User.objects.all()
    return render(request, 'estadisticas.html',{"sucursales":sucursales, "usuarios":usuarios})


@permission_required('pianoadherentes.can_view_stats_controllerAdmin', raise_exception=True)
def bajas_masivas(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Debe subir una planilla Excel.')

    archivo = request.FILES.get('archivo')
    if not archivo or not archivo.name.lower().endswith('.xlsx'):
        return HttpResponseBadRequest('Seleccione un archivo .xlsx con un CBU por fila.')

    try:
        origen = load_workbook(archivo, read_only=True, data_only=False)
        filas = list(origen.active.iter_rows(values_only=True))
        origen.close()
    except (InvalidFileException, BadZipFile, ValueError, OSError, KeyError, IndexError):
        return HttpResponseBadRequest('El archivo Excel no es valido.')

    if request.POST.get('vista_previa') == '1':
        filas_cargadas = sum(any(valor is not None and str(valor).strip() for valor in valores) for valores in filas)
        if not filas_cargadas:
            return HttpResponseBadRequest('El archivo Excel no contiene CBU.')
        cbus = {
            valores[0].strip() for valores in filas
            if valores and isinstance(valores[0], str)
            and len(valores[0].strip()) == 22 and valores[0].strip().isascii()
            and valores[0].strip().isdigit()
            and not any(valor is not None and str(valor).strip() for valor in valores[1:])
        }
        titulares = Titular.objects.filter(cbu__in=cbus)
        cantidad = titulares.filter(is_active=True).count() + Adherente.objects.filter(titular__in=titulares, is_active=True).count()
        return JsonResponse({'cantidad': cantidad, 'filas': filas_cargadas})

    resultado = Workbook()
    hoja = resultado.active
    hoja.title = 'Resultados'
    hoja.append(['Fila', 'CBU', 'Estado', 'Titular', 'Adherentes dados de baja',
                 'Adherentes ya inactivos', 'Detalle', 'Usuario', 'Fecha'])
    for numero, valores in enumerate(filas, start=1):
        cbu = str(valores[0]).strip() if valores and valores[0] is not None else ''
        if not any(valor is not None and str(valor).strip() for valor in valores):
            continue
        estado = 'CBU invalido'
        titular_estado = ''
        bajas = []
        inactivos = []
        detalle = 'Ingrese solamente un CBU de 22 digitos por fila, en celdas de texto.'
        fecha = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        if len(valores) == 1 or not any(valor is not None and str(valor).strip() for valor in valores[1:]):
            if isinstance(valores[0], str) and len(cbu) == 22 and cbu.isascii() and cbu.isdigit():
                try:
                    with transaction.atomic():
                        titular = Titular.objects.select_for_update().filter(cbu=cbu).first()
                        if titular is None:
                            estado = 'No encontrado'
                            detalle = 'No se encontro un titular con este CBU.'
                        else:
                            adherentes = list(Adherente.objects.select_for_update().filter(titular=titular))
                            titular_estado = 'Ya inactivo' if not titular.is_active else 'Dado de baja'
                            if titular.is_active:
                                titular.is_active = False
                                titular.deleted = timezone.now()
                                titular.user_upload = request.user
                                titular.save(update_fields=['is_active', 'deleted', 'user_upload'])
                            for adherente in adherentes:
                                if not adherente.is_active:
                                    inactivos.append(f'{adherente.name} {adherente.last_name}')
                                    continue
                                adherente.is_active = False
                                adherente.deleted = timezone.now()
                                adherente.user_upload = request.user
                                adherente.save(update_fields=['is_active', 'deleted', 'user_upload'])
                                Log.objects.create(adherente=adherente, movimiento='Baja', user=request.user)
                                bajas.append(f'{adherente.name} {adherente.last_name}')
                            estado = 'Ya estaban dados de baja' if titular_estado == 'Ya inactivo' and not bajas else 'Baja realizada'
                            detalle = f'Titular ID {titular.pk}; {len(adherentes)} adherentes encontrados.'
                except DatabaseError:
                    estado = 'Error'
                    titular_estado = ''
                    bajas = []
                    inactivos = []
                    detalle = 'No se realizaron cambios para este CBU por un error de base de datos.'
        hoja.append([numero, cbu, estado, titular_estado, ', '.join(bajas),
                     ', '.join(inactivos), detalle, request.user.username, fecha])
        hoja.cell(row=hoja.max_row, column=2).data_type = 's'

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="resultado_bajas_masivas.xlsx"'
    resultado.save(response)
    return response





@permission_required('pianoadherentes.can_view_stats', raise_exception=True)
def mis_ventas(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('init_date')
        end_date_str = request.POST.get('end_date')

        print(request.POST.get('init_date'))
        print(end_date_str)

        # Convertir las fechas de cadena a objetos datetime
        start_date_parts = start_date_str.split('-')
        start_date = '-'.join(start_date_parts)

        end_date_parts = end_date_str.split('-')
        end_date = '-'.join(end_date_parts)

        # Filtrar adherentes dentro del rango de fechas
        adherentes = Adherente.objects.filter(
            created__range=(start_date, end_date),
            user_upload=request.user)

        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'Adherentes'

        # Definir encabezados de columnas
        headers = [
            'Adherente ID',
            'Titular Nombre',
            'Titular Apellido',
            'Tipo de documento',
            'Documento',
            'CBU Titular',
            'Plan Titular',
            'Nombre',
            'Apellido',
            'Teléfono',
            'Dirección',
            'Plan Adherente',
            'Tipo documento',
            'Nro documento',
            'Fecha de Creación',
            'Usuario',
            'Sucursal'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, adherente in enumerate(adherentes, start=2):
            ws.cell(row=row_num, column=1, value=adherente.adherente_id)
            ws.cell(row=row_num, column=2, value=adherente.titular.name)
            ws.cell(row=row_num, column=3, value=adherente.titular.last_name)
            ws.cell(row=row_num, column=4, value=adherente.titular.document_type)
            ws.cell(row=row_num, column=5, value=adherente.titular.document)
            ws.cell(row=row_num, column=6, value=adherente.titular.cbu)
            ws.cell(row=row_num, column=7, value=adherente.titular.plan)
            ws.cell(row=row_num, column=8, value=adherente.name)
            ws.cell(row=row_num, column=9, value=adherente.last_name)
            ws.cell(row=row_num, column=10, value=adherente.phone)
            address_complete = str(f"{adherente.street_address} {adherente.number} {adherente.floor} - {adherente.city} - {adherente.province}")
            ws.cell(row=row_num, column=11, value=address_complete)
            ws.cell(row=row_num, column=12, value=adherente.plan)
            ws.cell(row=row_num, column=13, value=adherente.document_type)
            ws.cell(row=row_num, column=14, value=adherente.document)
            ws.cell(row=row_num, column=15, value=adherente.created.strftime('%Y-%m-%d %H:%M:%S'))
            ws.cell(row=row_num, column=16, value=adherente.user_upload.username)
            ws.cell(row=row_num, column=17, value=adherente.sucursal)

        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')




@permission_required('pianoadherentes.can_view_stats', raise_exception=True)
def mis_log(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('init_date')
        end_date_str = request.POST.get('end_date')

        # Convertir las fechas de cadena a objetos datetime
        start_date_parts = start_date_str.split('-')
        start_date = '-'.join(start_date_parts)

        end_date_parts = end_date_str.split('-')
        end_date = '-'.join(end_date_parts)

        # Filtrar adherentes dentro del rango de fechas

        log = Log.objects.filter(
            created__range=(start_date, end_date),
            user=request.user)

        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'My_log'

        # Definir encabezados de columnas
        headers = [
            'Log ID',
            'Adherente',
            'Movimiento',
            'Usuario',
            'Historia',
            'Fecha'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, log in enumerate(log, start=2):
            ws.cell(row=row_num, column=1, value=log.log_id)
            adherente = str(f'{log.adherente.name} {log.adherente.last_name}')
            ws.cell(row=row_num, column=2, value=adherente)
            ws.cell(row=row_num, column=3, value=log.movimiento)
            ws.cell(row=row_num, column=4, value=log.user.username)
            ws.cell(row=row_num, column=5, value=log.historia)
            ws.cell(row=row_num, column=6, value=log.created.strftime('%Y-%m-%d %H:%M:%S'))


        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')

def sucursal_ventas(request):
    if request.method == 'POST':
        print("llego hasta aca")
        start_date_str = request.POST.get('init_date')
        end_date_str = request.POST.get('end_date')
        sucursal = request.POST.get('sucursal')

        # Convertir las fechas de cadena a objetos datetime
        start_date_parts = start_date_str.split('-')
        start_date = '-'.join(start_date_parts)

        end_date_parts = end_date_str.split('-')
        end_date = '-'.join(end_date_parts)

        # Filtrar adherentes dentro del rango de fechas
        adherentes = Adherente.objects.filter(
            created__range=(start_date, end_date),
            sucursal=sucursal)

        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'Adherentes'

        # Definir encabezados de columnas
        headers = [
            'Adherente ID',
            'Titular Nombre',
            'Titular Apellido',
            'Tipo de documento',
            'Documento',
            'CBU Titular',
            'Plan Titular',
            'Nombre',
            'Apellido',
            'Teléfono',
            'Dirección',
            'Tipo documento',
            'Nro documento',
            'Plan Adherente',
            'Fecha de Creación',
            'Usuario',
            'Sucursal'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, adherente in enumerate(adherentes, start=2):
            ws.cell(row=row_num, column=1, value=adherente.adherente_id)
            ws.cell(row=row_num, column=2, value=adherente.titular.name)
            ws.cell(row=row_num, column=3, value=adherente.titular.last_name)
            ws.cell(row=row_num, column=4, value=adherente.titular.document_type)
            ws.cell(row=row_num, column=5, value=adherente.titular.document)
            ws.cell(row=row_num, column=6, value=adherente.titular.cbu)
            ws.cell(row=row_num, column=7, value=adherente.titular.plan)
            ws.cell(row=row_num, column=8, value=adherente.name)
            ws.cell(row=row_num, column=9, value=adherente.last_name)
            ws.cell(row=row_num, column=10, value=adherente.phone)
            address_complete = str(f"{adherente.street_address} {adherente.number} {adherente.floor} - {adherente.city} - {adherente.province}")
            ws.cell(row=row_num, column=11, value=address_complete)
            ws.cell(row=row_num, column=12, value=adherente.document_type)
            ws.cell(row=row_num, column=13, value=adherente.document)
            ws.cell(row=row_num, column=14, value=adherente.plan)
            ws.cell(row=row_num, column=15, value=adherente.created.strftime('%Y-%m-%d %H:%M:%S'))
            ws.cell(row=row_num, column=16, value=adherente.user_upload.username)
            ws.cell(row=row_num, column=17, value=adherente.sucursal)

        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')

@permission_required('pianoadherentes.can_view_stats', raise_exception=True)
def usuario_log(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('init_date')
        end_date_str = request.POST.get('end_date')
        usuario = request.POST.get('usuario')

        # Convertir las fechas de cadena a objetos datetime
        start_date_parts = start_date_str.split('-')
        start_date = '-'.join(start_date_parts)

        end_date_parts = end_date_str.split('-')
        end_date = '-'.join(end_date_parts)

        # Filtrar adherentes dentro del rango de fechas

        if usuario == None:
            log = Log.objects.filter(
                created__range=(start_date, end_date))
        else:
            log = Log.objects.filter(
                created__range=(start_date, end_date),
                user=usuario)

        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'Log por usuarios'

        # Definir encabezados de columnas
        headers = [
            'Log ID',
            'Adherente',
            'Movimiento',
            'Usuario',
            'Historia',
            'Fecha'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, log in enumerate(log, start=2):
            ws.cell(row=row_num, column=1, value=log.log_id)
            adherente = str(f'{log.adherente.name} {log.adherente.last_name} {log.adherente.document}')
            ws.cell(row=row_num, column=2, value=adherente)
            ws.cell(row=row_num, column=3, value=log.movimiento)
            ws.cell(row=row_num, column=4, value=log.user.username)
            ws.cell(row=row_num, column=5, value=log.historia)
            ws.cell(row=row_num, column=6, value=log.created.strftime('%Y-%m-%d %H:%M:%S'))


        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')


@permission_required('pianoadherentes.can_view_stats_controllerAdmin', raise_exception=True)
def padron_activo(request):

    if request.method == 'POST':
        adherentes = Adherente.objects.filter(is_active=1)
        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'Adherentes'
        # Definir encabezados de columnas
        headers = [
            'Adherente ID',
            'Titular Nombre',
            'Titular Apellido',
            'Tipo de documento',
            'Documento',
            'CBU Titular',
            'Plan Titular',
            'Nombre',
            'Apellido',
            'Teléfono',
            'Dirección',
            'Tipo documento',
            'Nro documento',
            'Plan Adherente',
            'Fecha de Creación',
            'Usuario',
            'Sucursal'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, adherente in enumerate(adherentes, start=2):
            ws.cell(row=row_num, column=1, value=adherente.adherente_id)
            ws.cell(row=row_num, column=2, value=adherente.titular.name)
            ws.cell(row=row_num, column=3, value=adherente.titular.last_name)
            ws.cell(row=row_num, column=4, value=adherente.titular.document_type)
            ws.cell(row=row_num, column=5, value=adherente.titular.document)
            ws.cell(row=row_num, column=6, value=adherente.titular.cbu)
            ws.cell(row=row_num, column=7, value=adherente.titular.plan)
            ws.cell(row=row_num, column=8, value=adherente.name)
            ws.cell(row=row_num, column=9, value=adherente.last_name)
            ws.cell(row=row_num, column=10, value=adherente.phone)
            address_complete = str(f"{adherente.street_address} {adherente.number} {adherente.floor} - {adherente.city} - {adherente.province}")
            ws.cell(row=row_num, column=11, value=address_complete)
            ws.cell(row=row_num, column=12, value=adherente.document_type)
            ws.cell(row=row_num, column=13, value=adherente.document)
            ws.cell(row=row_num, column=14, value=adherente.plan)
            if adherente.created:
                ws.cell(row=row_num, column=15, value=adherente.created.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                ws.cell(row=row_num, column=15, value='N/A')
            ws.cell(row=row_num, column=16, value=adherente.user_upload.username)
            ws.cell(row=row_num, column=17, value=adherente.sucursal)

        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')


@permission_required('pianoadherentes.can_view_stats_controllerAdmin', raise_exception=True)
def bajas(request):
    if request.method == 'POST':
        print("llego hasta aca")
        start_date_str = request.POST.get('init_date')
        end_date_str = request.POST.get('end_date')
        #sucursal = request.POST.get('sucursal')

        # Convertir las fechas de cadena a objetos datetime
        start_date_parts = start_date_str.split('-')
        start_date = '-'.join(start_date_parts)

        end_date_parts = end_date_str.split('-')
        end_date = '-'.join(end_date_parts)

        # Filtrar adherentes dentro del rango de fechas
        adherentes = Adherente.objects.filter(
            deleted__range=(start_date, end_date))

        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'Adherentes'

        # Definir encabezados de columnas
        headers = [
            'Adherente ID',
            'Titular Nombre',
            'Titular Apellido',
            'Tipo de documento',
            'Documento',
            'CBU Titular',
            'Plan Titular',
            'Nombre',
            'Apellido',
            'Teléfono',
            'Dirección',
            'Tipo documento',
            'Nro documento',
            'Plan Adherente',
            'Fecha de baja',
            'Usuario',
            'Sucursal'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, adherente in enumerate(adherentes, start=2):
            ws.cell(row=row_num, column=1, value=adherente.adherente_id)
            ws.cell(row=row_num, column=2, value=adherente.titular.name)
            ws.cell(row=row_num, column=3, value=adherente.titular.last_name)
            ws.cell(row=row_num, column=4, value=adherente.titular.document_type)
            ws.cell(row=row_num, column=5, value=adherente.titular.document)
            ws.cell(row=row_num, column=6, value=adherente.titular.cbu)
            ws.cell(row=row_num, column=7, value=adherente.titular.plan)
            ws.cell(row=row_num, column=8, value=adherente.name)
            ws.cell(row=row_num, column=9, value=adherente.last_name)
            ws.cell(row=row_num, column=10, value=adherente.phone)
            ws.cell(row=row_num, column=9, value=adherente.phone)
            address_complete = str(f"{adherente.street_address} {adherente.number} {adherente.floor} - {adherente.city} - {adherente.province}")
            ws.cell(row=row_num, column=11, value=address_complete)
            ws.cell(row=row_num, column=12, value=adherente.document_type)
            ws.cell(row=row_num, column=13, value=adherente.document)
            ws.cell(row=row_num, column=14, value=adherente.plan)
            ws.cell(row=row_num, column=15, value=adherente.deleted.strftime('%Y-%m-%d %H:%M:%S'))
            ws.cell(row=row_num, column=16, value=adherente.user_upload.username)
            ws.cell(row=row_num, column=17, value=adherente.sucursal)

        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')

def general_ventas(request):
    if request.method == 'POST':
        print("llego hasta aca")
        start_date_str = request.POST.get('init_date')
        end_date_str = request.POST.get('end_date')

        # Convertir las fechas de cadena a objetos datetime
        start_date_parts = start_date_str.split('-')
        start_date = '-'.join(start_date_parts)

        end_date_parts = end_date_str.split('-')
        end_date = '-'.join(end_date_parts)

        # Filtrar adherentes dentro del rango de fechas
        adherentes = Adherente.objects.filter(
            created__range=(start_date, end_date))

        # Crear un archivo Excel utilizando openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = 'Adherentes'

        # Definir encabezados de columnas
        headers = [
            'Adherente ID',
            'Titular Nombre',
            'Titular Apellido',
            'Tipo de documento',
            'Documento',
            'CBU Titular',
            'Plan Titular',
            'Nombre',
            'Apellido',
            'Teléfono',
            'Dirección',
            'Tipo documento',
            'Nro documento',
            'Plan Adherente',
            'Fecha de Creación',
            'Usuario',
            'Sucursal'
        ]

        # Escribir encabezados en la primera fila
        for col_num, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col_num, value=header)

        # Escribir datos de adherentes en filas
        for row_num, adherente in enumerate(adherentes, start=2):
            ws.cell(row=row_num, column=1, value=adherente.adherente_id)
            ws.cell(row=row_num, column=2, value=adherente.titular.name)
            ws.cell(row=row_num, column=3, value=adherente.titular.last_name)
            ws.cell(row=row_num, column=4, value=adherente.titular.document_type)
            ws.cell(row=row_num, column=5, value=adherente.titular.document)
            ws.cell(row=row_num, column=6, value=adherente.titular.cbu)
            ws.cell(row=row_num, column=7, value=adherente.titular.plan)
            ws.cell(row=row_num, column=8, value=adherente.name)
            ws.cell(row=row_num, column=9, value=adherente.last_name)
            ws.cell(row=row_num, column=10, value=adherente.phone)
            address_complete = str(f"{adherente.street_address} {adherente.number} {adherente.floor} - {adherente.city} - {adherente.province}")
            ws.cell(row=row_num, column=11, value=address_complete)
            ws.cell(row=row_num, column=12, value=adherente.document_type)
            ws.cell(row=row_num, column=13, value=adherente.document)
            ws.cell(row=row_num, column=14, value=adherente.plan)
            ws.cell(row=row_num, column=15, value=adherente.created.strftime('%Y-%m-%d %H:%M:%S'))
            ws.cell(row=row_num, column=16, value=adherente.user_upload.username)
            ws.cell(row=row_num, column=17, value=adherente.sucursal)

        # Crear el archivo Excel en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="informe.xlsx"'
        # Guardar el libro de trabajo en la respuesta HTTP
        wb.save(response)
        return response
    return render(request, 'estadisticas.html')
