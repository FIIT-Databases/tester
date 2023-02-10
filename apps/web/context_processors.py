from django.conf import settings


def info(context):
    return {
        'DEBUG': settings.DEBUG,
        'VERSION': settings.VERSION,
        'BUILD': settings.BUILD
    }
