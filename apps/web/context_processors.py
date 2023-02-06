import os

from django.conf import settings


def info(context):
    return {
        'DEBUG': settings.DEBUG,
        'VERSION': os.getenv('VERSION', 'DEV')
    }
