from django.http import HttpResponse
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.db import IntegrityError
from .forms import ClientForm , AdherenteForm, ClientFormPrestamos, ContratosForm

from .models import Titular , Adherente, Log, Prestamos, Contratos
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.conf import settings
from .utils.pass_generate import generate_random_password


def home(request):
    if request.user.is_authenticated:
        return redirect('select_cbu')
    return render(request, 'signin.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        print("este es el post del login")
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('create_client')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'Username already exists'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Password do not match'
        })

def recovery(request):
    if request.method == 'GET':
        
        return render(request, 'recovery_pass.html', {'form': AuthenticationForm})
    else:
        #logica para enviar la nueva contraseña
        username=request.POST['username']
        try:
            #instancio el objeto user
            user_obj =  User.objects.get(username=username)
            new_password = generate_random_password()
            print(new_password) 
            user_obj.set_password(str(new_password))
            user_obj.save()
            subject = 'Nueva contraseña'
            message = f'Su nueva contraseña es: {new_password}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_obj.email]

            send_mail(subject, message, email_from, recipient_list)
        except:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Usuario no encontrado'})
        return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Se envio una nueva contraseña a su correo electronico'})

def config(request):
    if request.method == 'GET':
        return render(request, 'config.html')
    else:
        #aca va la logica el cambio de contraseña
        user = authenticate(
            request, username=request.user, password=request.POST['password_old'])
        if user is None:
            return render(request, 'config.html', {'error': 'Usuario o pasword incorrecto'})
        else:
            if request.POST['password_new']== request.POST['password_new2']:
                user_obj =  User.objects.get(username=user)
                new_pass = request.POST['password_new']
                user_obj.set_password(str(new_pass))
                user_obj.save()
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Ingrese nuevamente'})

@login_required
def client(request):
    titulares = Titular.objects.filter(user_upload=request.user)
    return render(request, 'clients.html',{'titulares': titulares})

def signout(request):
    logout(request)
    return redirect('home')

def login_user(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Usuario o pasword incorrecto'})
        else:
            login(request, user)
            return redirect('select_cbu')

@login_required
def create_client(request):
    if request.method == 'GET':
        return render(request, 'create_client.html', {
            'form': ClientForm()
        })
    elif request.method == 'POST':
        try:
            form = ClientForm(request.POST)
            if form.is_valid():
                new_client = form.save(commit=False)
                new_client.user_upload = request.user
                new_client.save()
                return render(request, 'create_client.html', {
                    'new_client': new_client,
                    'form2': AdherenteForm()
                })
            else:
                # Mostrar los errores específicos del formulario
                print(form.errors)
                return render(request, 'create_client.html', {
                    'form': form,
                    'error': form.errors  # Muestra los errores del formulario
                })
        except ValueError as e:
            print(f"ValueError: {e}")
            return render(request, 'create_client.html', {
                'form': ClientForm(),
                'error': 'Please provide valid data'
            })
        except Exception as e:
            print(f"Unexpected error: {e}")
            return render(request, 'create_client.html', {
                'form': ClientForm(),
                'error': 'An unexpected error occurred'
            })

@login_required
def create_adherente(request):
    if request.method == 'POST':
        try:
            form = AdherenteForm(request.POST)
            if form.is_valid():
                titular_id = request.POST.get('titular_id')
                user_obj = User.objects.get(username=request.user)
                

                titular = Titular.objects.get(pk=titular_id)
                new_adherente = form.save(commit=False)
                new_adherente.user_upload = request.user
                new_adherente.titular = titular
                new_adherente.legajo = user_obj.datosuser.legajo
                new_adherente.sucursal  = user_obj.datosuser.sucursal.descripcion
                new_adherente.is_active = True
                new_adherente.save()

                Log.objects.create(
                    adherente=new_adherente,
                    movimiento='Creacion',
                    user=request.user
                )

                titular_id = request.POST.get('titular_id')
                new_client = Titular.objects.get(titular_id=titular_id)
                adherentes = Adherente.objects.filter(titular=titular_id)
                return render(request, 'create_client.html', {
                'new_client': new_client,
                'form2': form, # Redirigir a una vista de listado de clientes o a donde sea apropiado
                'tupla_adherentes': adherentes
                })
            else:
                raise ValueError
        except ValueError:
            titular_id = request.POST.get('titular_id')
            new_client = Titular.objects.get(titular_id=titular_id)
            return render(request, 'create_client.html', {
                'new_client': new_client,
                'form2': form,
                'error': 'Please provide valid data for adherente'
            })
    elif request.method == 'GET':
        titular_id = request.GET.get('titular_id')
        print(titular_id)
        new_client = Titular.objects.get(titular_id=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)
        return render(request, 'create_adherentes.html', {
                'new_client': new_client,
                'tupla_adherentes': adherentes
                })@login_required
def create_adherente(request):
    if request.method == 'POST':
        try:
            form = AdherenteForm(request.POST)
            if form.is_valid():
                titular_id = request.POST.get('titular_id')
                user_obj = User.objects.get(username=request.user)
                

                titular = Titular.objects.get(pk=titular_id)
                new_adherente = form.save(commit=False)
                new_adherente.user_upload = request.user
                new_adherente.titular = titular
                new_adherente.legajo = user_obj.datosuser.legajo
                new_adherente.sucursal  = user_obj.datosuser.sucursal.descripcion
                new_adherente.is_active = True
                new_adherente.save()

                Log.objects.create(
                    adherente=new_adherente,
                    movimiento='Creacion',
                    user=request.user
                )

                titular_id = request.POST.get('titular_id')
                new_client = Titular.objects.get(titular_id=titular_id)
                adherentes = Adherente.objects.filter(titular=titular_id)
                return render(request, 'create_client.html', {
                'new_client': new_client,
                'form2': form, # Redirigir a una vista de listado de clientes o a donde sea apropiado
                'tupla_adherentes': adherentes
                })
            else:
                raise ValueError
        except ValueError:
            titular_id = request.POST.get('titular_id')
            new_client = Titular.objects.get(titular_id=titular_id)
            return render(request, 'create_client.html', {
                'new_client': new_client,
                'form2': form,
                'error': 'Please provide valid data for adherente'
            })
    elif request.method == 'GET':
        titular_id = request.GET.get('titular_id')
        print(titular_id)
        new_client = Titular.objects.get(titular_id=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)
        return render(request, 'create_adherentes.html', {
                'new_client': new_client,
                'tupla_adherentes': adherentes
                })

@login_required
def client_detail(request, titular_id):
    if request.method == 'GET':
        #cliente = Titular.objects.filter(titular_id=titular_id)
        #titular = Titular.objects.get(pk=titular_id) esto puede tumbar el servidor
        titular = get_object_or_404(Titular,pk=titular_id)
        form = ClientForm(instance=titular)
        return render(request, 'client_detail.html',{'titular': titular, 'form': form})
    elif request.method == 'POST':
        try:
            titular = get_object_or_404(Titular,pk=titular_id)
            #titular = get_object_or_404(Titular,pk=titular_id,user_upload=request.user )
            form = ClientForm(request.POST, instance=titular)
            form.save()
            return redirect('clients')
        except ValueError:
            return render(request, 'client_detail.html',{'titular': titular, 'form': form, 'error': 'error actualizando cliente'})


@login_required
def client_baja(request,titular_id):
    titular = get_object_or_404(Titular, pk=titular_id)
    if request.method == 'POST':
        titular.is_active = False
        titular.deleted = timezone.now()
        titular.save()
        adherentes = Adherente.objects.filter(titular=titular_id)
        if adherentes:
                
            for adherente in adherentes:
                adherente.is_active = False
                adherente.deleted = timezone.now()
                adherente.user_upload = request.user
                user_obj = User.objects.get(username=request.user)
                adherente.sucursal  = user_obj.datosuser.sucursal.descripcion
                adherente.save()

                Log.objects.create(
                        adherente=adherente,
                        movimiento='Baja',
                        user=request.user
                    )

        return render(request, 'create_client.html', {
            'new_client': titular,
            'tupla_adherentes': adherentes
        })

@login_required
def consultar_cbu(request):
    if request.method == 'GET':
        return render(request, 'create_client_selCb.html', {
        })
    elif request.method == 'POST':
        cbu_r = request.POST.get("cbu")
        try:
            new_client = Titular.objects.get(cbu=cbu_r)
            try:
                titular_id = new_client.titular_id
                adherentes = Adherente.objects.filter(titular=titular_id)
                return render(request, 'create_client.html', {
                'new_client': new_client,
                'tupla_adherentes': adherentes,
                })
            except:
                return render(request, 'create_client.html', {
                'new_client': new_client,
                'cbu': cbu_r,
                })
        except Titular.DoesNotExist:
                return render(request, 'create_client.html', {
                'form': ClientForm(),
                'cbu': cbu_r,
            })

@login_required
def bajaAdherente(request, adherente_id):
    adherente = Adherente.objects.get(pk=adherente_id)
    if request.method == 'POST':
        adherente.is_active = False
        adherente.deleted = timezone.now()
        adherente.user_upload = request.user
        user_obj = User.objects.get(username=request.user)
        adherente.sucursal  = user_obj.datosuser.sucursal.descripcion
        adherente.save()

        titular_id = adherente.titular.pk  # Obtener el ID del titular correctamente
        new_client = get_object_or_404(Titular, pk=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)

        Log.objects.create(
                    adherente=adherente,
                    movimiento='Baja',
                    user=request.user
                )
        
        return render(request, 'create_client.html', {
            'new_client': new_client,
            'tupla_adherentes': adherentes
        })
    else:
        return HttpResponse("none")

@login_required
def reactiveAdherente(request, adherente_id):
    adherente = Adherente.objects.get(pk=adherente_id)
    if request.method == 'POST':
        adherente.is_active = True
        adherente.deleted = None
        adherente.user_upload = request.user
        user_obj = User.objects.get(username=request.user)
        adherente.sucursal  = user_obj.datosuser.sucursal.descripcion
        adherente.save()

        titular_id = adherente.titular.pk  # Obtener el ID del titular correctamente
        new_client = get_object_or_404(Titular, pk=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)

        Log.objects.create(
                    adherente=adherente,
                    movimiento='Reactivar',
                    user=request.user
                )
        
        return render(request, 'create_client.html', {
            'new_client': new_client,
            'tupla_adherentes': adherentes
        })
    else:
        return HttpResponse("none")


@login_required
def updateAdherente(request, adherente_id):
    adherente = Adherente.objects.get(pk=adherente_id)
    checklist = adherente.is_active
    if request.method == 'POST':
        form = AdherenteForm(request.POST, instance=adherente)
        if form.is_valid():
            form.save()

            titular_id = adherente.titular.titular_id
            adherentes = Adherente.objects.filter(titular=titular_id)
            user_obj = User.objects.get(username=request.user)
            adherente.sucursal  = user_obj.datosuser.sucursal.descripcion
            if checklist is True:
                adherente.deleted = None
            

            Log.objects.create(
                    adherente=adherente,
                    movimiento='Modificacion',
                    user=request.user
                )
            
            new_client = Titular.objects.get(pk=titular_id)
            return render(request, 'create_client.html', {
            'new_client': new_client,
            'tupla_adherentes': adherentes
            })
    else:
        form = AdherenteForm(instance=adherente)

    return render(request, 'update_adherente.html', {'adherente': adherente, 'form': form, 'is_active': checklist})

@login_required
def update_titular(request, titular_id):
    titular = get_object_or_404(Titular, pk=titular_id)
    checklist = titular.is_active
    print(titular.__dict__) 
    form = ClientForm(request.POST, instance=titular)

    if request.method == 'POST':

        if form.is_valid():
            
            form.save()
            adherentes = Adherente.objects.filter(titular=titular)
            return render(request, 'create_client.html', {
            'new_client': titular,
            'tupla_adherentes': adherentes
            }) # Redirigir después de guardar
        else:
            form = ClientForm(instance=titular)
            print(titular.between_street)
            print("Formulario inválido", form.errors)

    elif request.method == 'GET':
        pass
    return render(request, 'update_client.html', {'client': titular, 'form': form, 'is_active' : checklist})

@login_required
def buscar(request):
    if request.method == 'GET':
        return render(request, 'buscar.html')
    elif request.method == 'POST':
        cbu = request.POST.get('cbu')
        nombre = request.POST.get('name')
        apellido = request.POST.get('last_name')
        nro_doc = request.POST.get('document')
        street_address = request.POST.get('street_address')
        
        number = request.POST.get('number')
        floor = request.POST.get('floor')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')
        

        if not any([cbu, nombre, apellido, nro_doc, street_address, number, floor, city, postal_code, phone]):
                    return render(request, 'buscar.html', {
                        'error': 'Debe proporcionar al menos un criterio de búsqueda.'
                    })

        filtro = {}

        if cbu:
            filtro['cbu'] = cbu
        if nombre:
            filtro['name__icontains'] = nombre
        if apellido:
            filtro['last_name__icontains'] = apellido
        if nro_doc:
            filtro['document'] = nro_doc
        if street_address:
            filtro['street_address__icontains'] = street_address
        if number:
            filtro['number'] = number
        if floor:
            filtro['floor'] = floor
        if city:
            filtro['city'] = city
        if postal_code:
            filtro['postal_code'] = postal_code
        if phone:
            filtro['phone'] = phone


        titulares = Titular.objects.filter(**filtro)
        if titulares.exists():

            return render(request, 'list_client.html', {
                'new_client': titulares
            })
        else:
            # Manejar el caso en que no se encuentren titulares
            return render(request, 'list_client.html', {
                'new_client': None,
                'error': 'No se encontraron titulares con los datos proporcionados.'
            })

@login_required
def print_form(request):
    titular_id = request.GET.get('titular_id')
    activos = request.GET.get('is_active')
    if activos=="true":
        client = Titular.objects.get(titular_id=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)
    else:
        client = Titular.objects.get(titular_id=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id, is_active=1)

    return render(request, 'formulario.html', {'titular': client, 'adherentes' : adherentes})


@login_required
def consultar_cuil(request):
    if request.method == 'GET':
        print("ESTOY EN CONSuLLTAR CUIL GET")
        return render(request, 'create_client_selCuil.html', {
        })
    elif request.method == 'POST':
        cuil_r = request.POST.get("cuil")
        try:
            new_client = Prestamos.objects.get(document=cuil_r)
            try:
                
                titular_id = new_client.prestamos_id
                contratos = Contratos.objects.filter(titular_prestamo=titular_id)
                return render(request, 'create_client_prestamos.html', {
                'new_client': new_client,
                'tupla_contratos': contratos,
                })
            except:
                
                return render(request, 'create_client_prestamos.html', {
                'new_client': new_client,
                'cbu': cuil_r,
                })
        except Prestamos.DoesNotExist:
                print(cuil_r)
                print("ESTOY EN CONSuLLTAR CUIL POST")
                return render(request, 'create_client_prestamos.html', {
                'form': ClientForm(),
                'cuil': cuil_r,
            })
        



@login_required
def create_client_prestamo(request):
    if request.method == 'GET':
        return render(request, 'create_client_prestamos.html', {
            'form': ClientForm()
        })
    elif request.method == 'POST':
        try:
            form = ClientFormPrestamos(request.POST)
            if form.is_valid():
                new_client = form.save(commit=False)
                new_client.user_upload = request.user
                new_client.save()
                return render(request, 'create_client_prestamos.html', {
                    'new_client': new_client,
                    'form2': ClientFormPrestamos()
                })
            else:
                # Mostrar los errores específicos del formulario
                print(form.errors)
                return render(request, 'create_client_prestamos.html', {
                    'form': form,
                    'error': form.errors  # Muestra los errores del formulario
                })
        except ValueError as e:
            print(f"ValueError: {e}")
            return render(request, 'create_client.html', {
                'form': ClientForm(),
                'error': 'Please provide valid data'
            })
        except Exception as e:
            print(f"Unexpected error: {e}")
            return render(request, 'create_client.html', {
                'form': ClientForm(),
                'error': 'An unexpected error occurred'
            })


@login_required
def create_contract(request):
    if request.method == 'POST':
        try:
            form = ContratosForm(request.POST)
            if form.is_valid():
                prestamo_titular_id = request.POST.get('prestamo_id')
                user_obj = User.objects.get(username=request.user)
                

                prestamo_titular = Prestamos.objects.get(pk=prestamo_titular_id)
                new_contract = form.save(commit=False)
                new_contract.user_upload = request.user
                new_contract.titular_prestamo = prestamo_titular
                new_contract.legajo = user_obj.datosuser.legajo
                new_contract.sucursal  = user_obj.datosuser.sucursal.descripcion
                new_contract.is_active = True
                new_contract.save()
                """
                Log.objects.create(
                    adherente=new_adherente,
                    movimiento='Creacion',
                    user=request.user
                )"""
                ###HASTA ACA LLEGUE
            
                titular_id = request.POST.get('titular_id')
                new_client = Titular.objects.get(titular_id=titular_id)
                adherentes = Adherente.objects.filter(titular=titular_id)
                return render(request, 'create_client.html', {
                'new_client': new_client,
                'form2': form, # Redirigir a una vista de listado de clientes o a donde sea apropiado
                'tupla_adherentes': adherentes
                })
            else:
                raise ValueError
        except ValueError:
            titular_id = request.POST.get('titular_id')
            new_client = Titular.objects.get(titular_id=titular_id)
            return render(request, 'create_client.html', {
                'new_client': new_client,
                'form2': form,
                'error': 'Please provide valid data for adherente'
            })
    elif request.method == 'GET':
        titular_id = request.GET.get('titular_id')
        print(titular_id)
        new_client = Titular.objects.get(titular_id=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)
        return render(request, 'create_adherentes.html', {
                'new_client': new_client,
                'tupla_adherentes': adherentes
                })