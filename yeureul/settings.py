"""
Django settings for yeureul project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from typing import Dict

from django.core.exceptions import ImproperlyConfigured
import dj_database_url
# import paydunya
import django_heroku


# get the environment variable
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('SECRET_KEY')

DEBUG = True
if DEBUG:
    BASE_URL = 'http://localhost:8000/'
else:
    BASE_URL = 'https://yerel.heroku.com/'

# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'yerel.heroku.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yeureul',
    'ads.apps.AdsConfig',
    'pricing.apps.PricingConfig',
    'widget_tweaks',
    'simple_history',
    'reversion',
    'django_elasticsearch_dsl',
    'django_cleanup'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'yeureul.urls'

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

WSGI_APPLICATION = 'yeureul.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {'default': dj_database_url.config()}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# REST global settings
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.registration` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    # Add to this list all the locations containing your static files
)
LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'yeureul01@gmail.com'
EMAIL_HOST_PASSWORD = 'yeureul123'

# PayDunya config #####

# Activer le mode 'test'. Le debug est à False par défaut
# if DEBUG:
#     paydunya.debug = True
#     PAYDUNYA_ACCESS_TOKENS: Dict[str, str] = {
#         'PAYDUNYA-MASTER-KEY': "4xhWbWkN-ahcQ-dQrZ-trfq-4rbCkcl1dGUe",
#         'PAYDUNYA-PRIVATE-KEY': "test_private_Wys1xQyOzpyZLv3xfnewupdtNAg",
#         'PAYDUNYA-TOKEN': "XVD9DqykJBgGxp2XpgdD"
#     }
# else:
#     PAYDUNYA_ACCESS_TOKENS: Dict[str, str] = {
#         'PAYDUNYA-MASTER-KEY': "4xhWbWkN-ahcQ-dQrZ-trfq-4rbCkcl1dGUe",
#         'PAYDUNYA-PRIVATE-KEY': "live_private_lXejvZ8piTeXdzD6EKSTdQyeJcH",
#         'PAYDUNYA-TOKEN': "fqymhtMub4lbUQAlIuy4"
#     }
#
# # Configurer les clés d'API
# paydunya.api_keys = PAYDUNYA_ACCESS_TOKENS
#
# OPR = dict()
# end paydunya config  #####

# elasticsearch_dsl config
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
django_heroku.settings(locals())
