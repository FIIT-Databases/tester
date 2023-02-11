import django_rq
from django.conf import settings
from django.utils import timezone
from django.views import View

from apps.api.response import SingleResponse
from apps.core.models import Task


class StatusManagement(View):
    def get(self, request):
        queue = django_rq.get_queue('default')

        response = {
            'timestamp': timezone.now(),
            'instance': settings.INSTANCE_NAME,
            'stats': {
                'queue': queue.count,
                'tests': Task.objects.filter(executor=Task.Executor.FORM).count(),
            },
            'build': settings.BUILD,
            'version': settings.VERSION
        }
        return SingleResponse(request, response)
