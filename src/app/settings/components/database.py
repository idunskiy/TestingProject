# from app.settings.base import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'HOST': os.environ['DB_HOST'],
        'USER': os.environ['DB_USER'],
        'PASS': os.environ['DB_PASS'],
    }
}