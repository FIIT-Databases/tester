import csv
import uuid

import django_rq
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.jobs import basic_job
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
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    links = models.FileField(storage=private_storage, upload_to=_upload_to_path)
    tasks = models.ManyToManyField(Task)

    def is_done(self) -> bool:
        return not self.tasks.filter(status=Task.Status.PENDING).exists()

    def __str__(self) -> str:
        return f"{self.assignment.name} - {self.created_at.strftime('%Y-%m-%d')}"


@receiver(post_save, sender=Evaluation)
def execute_tasks(sender, instance: Evaluation, created: bool, **kwargs):
    if created:
        with open(instance.links.path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                task = Task.objects.create(
                    user=instance.creator,
                    assigment=instance.assignment,
                    executor=Task.Executor.EVALUATION,
                    image=row["Link"],
                    additional_information=row,
                )
                instance.tasks.add(task)
                django_rq.enqueue(basic_job, task.pk, False)


__all__ = ["Evaluation"]
