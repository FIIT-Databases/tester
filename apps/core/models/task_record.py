from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.core.models.base import BaseModel
from apps.core.models.scenario import Scenario
from apps.core.models.task import Task


class TaskRecord(BaseModel):
    class Meta:
        app_label = "core"
        db_table = "task_records"
        default_permissions = ()

    class Status(models.TextChoices):
        OK = "ok", _("OK")
        INVALID = "invalid", _("Invalid")
        TIMEOUT = "timeout", _("Timeout")
        ERROR = "error", _("4xx or 500x")

    class DiffType(models.TextChoices):
        HTML = "html", _("HTML")
        FILE = "file", _("file")

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="records")
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="+")
    status = models.CharField(choices=Status.choices, max_length=20)
    url = models.URLField()
    response = models.TextField(null=True)
    diff = models.TextField(null=True)
    diff_type = models.TextField(choices=DiffType.choices, max_length=15, null=True)
    messages = models.JSONField(default=list)
    duration = models.DurationField(null=True)
    additional_data = models.JSONField(default=dict)


__all__ = ["TaskRecord"]
