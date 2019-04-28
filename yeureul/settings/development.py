from .base import *


ALLOWED_HOSTS = ['localhost', '127.0.0.1']

BASE_URL = 'http://localhost:8000/'

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
        'NAME': 'yeureul',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


# elasticsearch_dsl config
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
