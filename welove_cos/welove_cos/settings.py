"""
Django settings for welove_cos project.

Generated by 'django-admin startproject' using Django 2.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError:
    try:
        from . import secret_settings
        SECRET_KEY = secret_settings.secret_key
    except ImportError:
        print(
            "WARNING: Cannot import secret_settings. Using development values."
        )
        # SECURITY WARNING: keep the secret key used in production secret!
        SECRET_KEY = 'e*n7&$5k)587^#)$&v#qw4xl8kyb-*0pb)v0k1)losjnuireiu'

ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

if not DEBUG:

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'raven.contrib.django.raven_compat',
    'quotes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'welove_cos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

TEMPLATES[0]['OPTIONS']['context_processors'].append(
        "quotes.context_processors.quotes_processor"
    )

WSGI_APPLICATION = 'welove_cos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'welove_cosdb',
        'USER': 'cos_lover',
        'PASSWORD': 'loveoverfear',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'profile'

SITE_DOMAIN = 'welovecityofsound.herokuapp.com'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

ADMINS = [('Ana Isabel', 'cmanaisabel7@gmail.com')]


try:
    CELERY_BROKER_URL = os.environ['REDIS_URL']
except KeyError:
    CELERY_BROKER_URL = 'redis://'

CELERY_IMPORTS = ['quotes']

# Email settings
try:
    email_user = os.environ["EMAIL_SETTINGS_USER"]
    email_password = os.environ["EMAIL_SETTINGS_PASSWORD"]
except KeyError:
    from . import email_settings
    email_user = email_settings.email
    email_password = email_settings.password
except ImportError:
    raise ImportError(
        "Cannot import email_settings.  See ../tools/create_email_settings.py"
    )

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = email_user
EMAIL_HOST_PASSWORD = email_password
EMAIL_PORT = 587

# Activate Django-Heroku.
django_heroku.settings(locals())
