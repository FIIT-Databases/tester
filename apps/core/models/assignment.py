from django.db import models

from apps.core.models.base import BaseModel


class Assignment(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'assignments'
        default_permissions = ()

    name = models.CharField(max_length=200)
    database = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


__all__ = [
    'Assignment'
]
