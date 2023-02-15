from uuid import UUID

from django.core.management import BaseCommand
from django.utils import timezone

from apps.core import jobs
from apps.core.models import Assignment, Task


class Command(BaseCommand):
    help = 'Create and execute task manually'

    def add_arguments(self, parser):
        parser.add_argument("--assignment", type=UUID)
        parser.add_argument("--image", type=str)

    def handle(self, *args, **options):
        started_at = timezone.now()
        self.stdout.write(f"Started: {started_at.isoformat()}")

        try:
            assignment = Assignment.objects.get(pk=options['assignment'])
        except Assignment.DoesNotExist:
            self.stdout.write(self.style.ERROR('Assignment does not exist!'))
            return False

        task = Task.objects.create(
            assigment=assignment,
            image=options['image'],
            executor=Task.Executor.JOB
        )

        task = jobs.BasicJob.execute(task_id=task.pk, public_only=False)
        self.stdout.write(f"Result: {task.status}")

        self.stdout.write(f"Finished: {timezone.now().isoformat()}")
        self.stdout.write(f"Duration: {timezone.now() - started_at}")
