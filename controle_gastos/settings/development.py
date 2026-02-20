from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["snfin.samukaoliveira.com.br", "localhost", "127.0.0.1", "134.255.176.164"]

CSRF_TRUSTED_ORIGINS = [
    "https://snfin.samukaoliveira.com.br",
    "http://134.255.176.164:7000",
]


SECRET_KEY = "django-insecure-dev-only"

INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']



