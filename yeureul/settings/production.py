import dj_database_url
import django_heroku

from .base import *

DEBUG = False
BASE_URL = 'https://yerel.heroku.com/'

# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'yerel.heroku.com']

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {'default': dj_database_url.config()}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


# elasticsearch_dsl config
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'https://m0l4tc8844:3bpgklxhyq@birch-220453499.eu-west-1.bonsaisearch.net'
    },
}
django_heroku.settings(locals())
