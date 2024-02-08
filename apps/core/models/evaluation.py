import uuid

from django.db import models

from apps.core.models.assignment import Assignment
from apps.core.models.task import Task
from apps.core.models.base import BaseModel, private_storage


class Evaluation(BaseModel):
    class Meta:
        app_label = "core"
        db_table = "evaluations"
        default_permissions = ("add",)

    def _upload_to_path(self, filename):
        return f"evaluations/{uuid.uuid4()}_{filename}"

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    links = models.FileField(storage=private_storage, upload_to=_upload_to_path)
    tasks = models.ManyToManyField(Task)

    def is_done(self) -> bool:
        return not self.tasks.filter(status=Task.Status.PENDING).exists()

    def __str__(self) -> str:
        return f"{self.assignment.name} - {self.created_at.strftime('%Y-%m-%d')}"


__all__ = ["Evaluation"]
