"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pianoadherentes import views
from pianoadherentes.stats.stats import mis_ventas, estadisticas, mis_log, sucursal_ventas, usuario_log , padron_activo, bajas, general_ventas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('signup/',views.signup, name='signup'),
    path('recovery_pass/',views.recovery, name='recovery_pass'),
    path('config/',views.config, name='config'),

    path('client/',views.client, name='clients'),
    path('client/find/',views.buscar, name='buscar'),
    path('client/update/<int:titular_id>/', views.update_titular, name='update_titular'),
    path('client/create/',views.create_client, name='create_client'),
    path('client/create/select_cbu/',views.consultar_cbu, name='select_cbu'),
    path('client/<int:titular_id>/',views.client_detail, name='client_detail'),
    path('client/<int:titular_id>/baja/',views.client_baja, name='client_baja'),
    path('client/adherente/create/',views.create_adherente, name='create_adherente'),
    path('adherente/baja/<int:adherente_id>/', views.bajaAdherente, name='baja_adherente'),
    path('adherente/update/<int:adherente_id>/', views.updateAdherente, name='update_adherente'),
    path('adherente/reactiv_adherente/<int:adherente_id>/', views.reactiveAdherente, name='reactiv_adherente'),
    path('stats/',estadisticas, name='stats'),
    path('stats/my_sales/',mis_ventas, name='my_sales'),
    path('stats/my_log/',mis_log, name='my_log'),
    path('stats/branch_office/',sucursal_ventas, name='branch_office'),
    path('stats/branch_general/',general_ventas, name='branch_general'),
    path('stats/user_log/',usuario_log, name='user_log'),
    path('stats/roll/',padron_activo, name='roll_active'),
    path('stats/removal/',bajas, name='removal'),



    path('logout/',views.signout, name='logout'),
    path('signin/',views.login_user, name='signin'),

    path('signin/',views.login_user, name='signin'),
    path('print_form/',views.print_form, name='print_form'),

    path('adherente-info/', views.get_adherente_info, name='get_user_info'),

    path('padron/', views.padron_consulta, name='padron'),
]
