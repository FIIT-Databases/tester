from .base import *

TIME_ZONE = 'Europe/Bratislava'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(';')

CSRF_TRUSTED_ORIGINS = [
    BASE_URL
]
