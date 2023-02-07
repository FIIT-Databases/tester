from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.core.models.assignment import Assignment
from apps.core.models.base import BaseModel


class Scenario(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'scenarios'
        default_permissions = ()

    class Method(models.TextChoices):
        GET = 'GET', 'GET'
        POST = 'POST', 'POST'
        PUT = 'PUT', 'PUT'
        PATCH = 'PATCH', 'PATCH'
        DELETE = 'DELETE', 'DELETE'

    assigment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='scenarios')
    url = models.CharField(max_length=200, help_text=_('Endpoint handle (/v1/hello)'))
    method = models.CharField(choices=Method.choices, help_text=_('HTTP method'), max_length=10, default=Method.GET)
    response = models.JSONField()
    body = models.JSONField(null=True, help_text=_('HTTP body'), blank=True)
    is_public = models.BooleanField(default=False, help_text=_('Scenario publicity'))

    def __str__(self) -> str:
        return f"{self.assigment.name} - {self.url}"


__all__ = [
    'Scenario'
]
