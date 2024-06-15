from django.http import HttpResponse
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.db import IntegrityError
from .forms import ClientForm , AdherenteForm
from django.contrib import messages
from .models import Titular , Adherente
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'signin.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
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
    print(request.method)
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
                raise ValueError("Invalid form data")
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
                titular = Titular.objects.get(pk=titular_id)
                new_adherente = form.save(commit=False)
                new_adherente.user_upload = request.user
                new_adherente.titular = titular
                new_adherente.save()
                titular_id = request.POST.get('titular_id')
                new_client = Titular.objects.get(titular_id=titular_id)
                adherentes = Adherente.objects.filter(titular=titular_id)
                print(adherentes)
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
        return render(request, 'create_client.html', {
            'new_client': titular,
            'tupla_adherentes': adherentes
        })

@login_required
def consultar_cbu(request):
    if request.method == 'GET':
        return render(request, 'create_client_selCB.html', {
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
    print(adherente.adherente_date)
    if request.method == 'POST':
        adherente.is_active = False
        adherente.save()

        titular_id = adherente.titular.pk  # Obtener el ID del titular correctamente
        new_client = get_object_or_404(Titular, pk=titular_id)
        adherentes = Adherente.objects.filter(titular=titular_id)

        return render(request, 'create_client.html', {
            'new_client': new_client,
            'tupla_adherentes': adherentes
        })
    else:
        return HttpResponse("none")
    
def updateAdherente(request, adherente_id):
    adherente = Adherente.objects.get(pk=adherente_id)
    checklist = adherente.is_active
    if request.method == 'POST':
        form = AdherenteForm(request.POST, instance=adherente)
        if form.is_valid():
            form.save()
            print(adherente.is_active)
            titular_id = adherente.titular.titular_id
            adherentes = Adherente.objects.filter(titular=titular_id)
            print(titular_id)
            new_client = Titular.objects.get(pk=titular_id)
            return render(request, 'create_client.html', {
            'new_client': new_client,
            'tupla_adherentes': adherentes
            })
    else:
        form = AdherenteForm(instance=adherente)
    
    return render(request, 'update_adherente.html', {'adherente': adherente, 'form': form, 'is_active': checklist})


def update_titular(request, titular_id):
    titular = get_object_or_404(Titular, pk=titular_id)
    checklist = titular.is_active
    print(titular.is_active)
    if request.method == 'POST':
        print("aca metodo post") 
        form = ClientForm(request.POST, instance=titular)
        if form.is_valid():
            print("aca metodo post y formulario valido") 
            
            
            form.save()
            adherentes = Adherente.objects.filter(titular=titular)
            return render(request, 'create_client.html', {
            'new_client': titular,
            'tupla_adherentes': adherentes
            }) # Redirigir después de guardar
        else:
            print("aca es donde paso el valor") 
            form = ClientForm(instance=titular)
        
    return render(request, 'update_client.html', {'client': titular, 'form': form, 'is_active' : checklist})

def buscar(request):
    if request.method == 'GET':
        return render(request, 'buscar.html')
    elif request.method == 'POST':
        nombre = request.POST.get('name')
        telefono = request.POST.get('phone')
        direccion = request.POST.get('address')
        dni = request.POST.get('dni')
        activo = request.POST.get('is_active')
        cbu = request.POST.get('cbu')


        if not any([cbu, nombre, telefono, direccion, dni]):
                    return render(request, 'buscar.html', {
                        'error': 'Debe proporcionar al menos un criterio de búsqueda.'
                    })
        
        filtro = {}
        print("este es el cbu: " ,cbu)
        if cbu:
            filtro['cbu'] = cbu
        if nombre:
            filtro['name__icontains'] = nombre
        if telefono:
            filtro['phone'] = telefono
        if direccion:
            filtro['address__icontains'] = direccion
        if dni:
            filtro['dni'] = dni
        if activo:
            filtro['is_active'] = True
        
        print(filtro)

        titulares = Titular.objects.filter(**filtro)
        if titulares.exists():
            print(titulares)
            return render(request, 'list_client.html', {
                'new_client': titulares
            })
        else:
            # Manejar el caso en que no se encuentren titulares
            return render(request, 'list_client.html', {
                'new_client': None,
                'error': 'No se encontraron titulares con los datos proporcionados.'
            })



