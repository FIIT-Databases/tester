from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from apps.core.models.assignment import Assignment
from apps.core.models.base import BaseModel


class Task(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'tasks'
        default_permissions = ()

    class Status(models.TextChoices):
        PENDING = 'pending', _('pending')
        DONE = 'done', _('done')
        FAILED = 'failed', _('failed')

    class Executor(models.TextChoices):
        FORM = 'form', _('form')
        JOB = 'job', _('job')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    assigment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(choices=Status.choices, default=Status.PENDING, max_length=15)
    executor = models.CharField(choices=Executor.choices, default=Executor.FORM, max_length=15)
    image = models.CharField(
        help_text=_(
            'Path to GitHub hosted docker image. Example: ghcr.io/fiit-databases/dbs-python-example:master'
        ),
        verbose_name=_('Docker Image'),
        max_length=255
    )
    message = models.TextField(null=True, editable=False)
    output = models.TextField(null=True, editable=False)

    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'task_id': self.pk})

    def __str__(self):
        return f"{self.assigment.name} - {self.user.username} ({self.id})"


__all__ = [
    'Task'
]
