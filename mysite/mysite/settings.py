"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', default='your secret key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['fsuarez.pythonanywhere.com', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'admin_interface',
    'pianoadherentes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'colorfield',
]

X_FRAME_OPTIONS='SAMEORIGIN'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

if DEBUG == True:
    STATICFILES_DIRS = [
        BASE_DIR / "pianoadherentes/static",
    ]
else:
    STATICFILES_DIRS = [
        '/home/fsuarez/Ayuda-App/mysite/pianoadherentes/static/',
        '/home/fsuarez/Ayuda-App/mysite/static/'
    ]

# Ruta donde se recopilarán los archivos estáticos al ejecutar collectstatic
if DEBUG == True:
    STATIC_ROOT = BASE_DIR / "staticfiles"
else:
    STATIC_ROOT = '/home/fsuarez/Ayuda-App/mysite/static/'



LOGIN_URL = '/signin'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



#configuraciones del token

SESSION_COOKIE_AGE = 14400

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#SESSION_SAVE_EVERY_REQUEST = True


#CSRF_COOKIE_SECURE = True

if DEBUG == False:
    SESSION_SAVE_EVERY_REQUEST = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    APP_DIRS=True


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


############ENVIO DE CORREOS CONFIGURACION ########################### ESTO LO TENGO QUE PROTEGER


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Servidor SMTP de tu proveedor de correo
EMAIL_PORT = 587  # Puerto para conexión TLS
EMAIL_USE_TLS = True  # Activa el cifrado TLS
EMAIL_HOST_USER = 'appayudamedica@gmail.com'  # Tu correo
EMAIL_HOST_PASSWORD = 'nxuw nagm mnwr gtwx'  # Tu contraseña de aplicación o correo
DEFAULT_FROM_EMAIL = 'appayudamedica@gmail.com'  # Remitente por defecto