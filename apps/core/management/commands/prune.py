import docker
from django.core.management import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Prune unused docker images'

    def handle(self, *args, **options):
        started_at = timezone.now()
        self.stdout.write(f"Started: {started_at.isoformat()}")

        client = docker.from_env()  # FIXME: asi tazko
        client.images.prune(filters={'dangling': False})

        self.stdout.write(f"Finished: {timezone.now().isoformat()}")
        self.stdout.write(f"Duration: {timezone.now() - started_at}")
