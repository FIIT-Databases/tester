from django.db import models

from apps.core.models.assignment import Assignment
from apps.core.models.base import BaseModel


class Scenario(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'scenarios'
        default_permissions = ()

    assigment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='scenarios')
    url = models.CharField(max_length=200)
    response = models.JSONField()
    is_public = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.assigment.name} - {self.url}"


__all__ = [
    'Scenario'
]
