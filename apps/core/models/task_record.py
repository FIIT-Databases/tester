from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.core.models.base import BaseModel
from apps.core.models.scenario import Scenario
from apps.core.models.task import Task


class TaskRecord(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'task_records'
        default_permissions = ()

    class Status(models.TextChoices):
        OK = 'ok', _('OK')
        INVALID_JSON = 'invalid_json', _('parse error or invalid content-type')
        INVALID_HTTP_STATUS = 'invalid_http_status', _('invalid http status code')
        TIMEOUT = 'timeout', _('timeout')
        MISMATCH = 'mismatch', _('response do not match')
        ERROR = 'error', _('4xx or 500x')

    class DiffType(models.TextChoices):
        HTML = 'html', _('HTML')
        FILE = 'file', _('file')

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='records')
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='+')
    status = models.CharField(choices=Status.choices, max_length=20)
    url = models.URLField()
    response = models.TextField(null=True)
    diff = models.TextField(null=True)
    diff_type = models.TextField(choices=DiffType.choices, max_length=15, null=True)
    message = models.TextField()
    duration = models.DurationField(null=True)
    additional_data = models.JSONField(default=dict)


__all__ = [
    'TaskRecord'
]
