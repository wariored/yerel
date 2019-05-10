from .base import *

# DEBUG = False
BASE_URL = 'https://yerel.co/'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yerel.co']


# Application definition

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'postgres',
        'PASSWORD': 'postgre',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'NAME': 'yerel',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


# elasticsearch_dsl config
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
