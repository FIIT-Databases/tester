import docker
from django.core.management import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.core.models import Task


class Command(BaseCommand):
    help = "Prune unused docker containers/images and databases"

    def handle(self, *args, **options):
        started_at = timezone.now()
        self.stdout.write(f"Started: {started_at.isoformat()}")

        client = docker.from_env()
        client.containers.prune()
        client.images.prune(filters={"dangling": False, "until": "5m"})

        for task in Task.objects.filter(status=Task.Status.FAILED, additional_information__database__isnull=False):
            with connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS {task.additional_information['database']['name']};")
                cursor.execute(f"DROP USER IF EXISTS {task.additional_information['database']['name']};")
                connection.commit()

        self.stdout.write(f"Finished: {timezone.now().isoformat()}")
        self.stdout.write(f"Duration: {timezone.now() - started_at}")
