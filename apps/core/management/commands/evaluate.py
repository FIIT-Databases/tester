import csv
import pathlib
import time
from uuid import UUID

import requests
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from requests import ReadTimeout

from apps.core import jobs
from apps.core.models import Assignment, Task


class Command(BaseCommand):
    help = 'Evaluate the assignments according to the input file'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self._students = {}
        self._assignment = None

    def add_arguments(self, parser):
        parser.add_argument('--wake-up', action='store_true', default=False)
        parser.add_argument("--assignment", type=UUID)
        parser.add_argument("--source", type=pathlib.Path)
        parser.add_argument("--output", type=pathlib.Path, default='zadanie2.results.csv')

    def handle(self, *args, **options):
        started_at = timezone.now()
        self.stdout.write(f"Started: {started_at.isoformat()}")

        try:
            self._assignment = Assignment.objects.get(pk=options['assignment'])
        except Assignment.DoesNotExist:
            self.stdout.write(self.style.ERROR('Assignment does not exist!'))
            return False

        self.stdout.write("Reading sutdents")
        with open(options['source'], 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            for row in reader:
                self._students[row['Link']] = {
                    'email': str(row['Email']).strip(),
                    'link': str(row['Link']).strip(),
                    'course': str(row['Course']).strip(),
                }

        if options['wake_up']:
            self.wake_up()

        self.stdout.write("Performing test scenarios")

        for student_email in self._students.keys():
            task = Task.objects.create(
                assigment=self._assignment,
                image=self._students[student_email]['link'],
                executor=Task.Executor.JOB
            )
            self._students[student_email]['result'] = f"{settings.BASE_URL}{task.get_absolute_url()}"
            self.stdout.write(f"{student_email} ({task.id})")
            task = jobs.BasicJob.execute(task_id=task.pk, public_only=False)
            for record in task.records.all():
                self._students[student_email][record.scenario.url] = record.status

        with open(options['output'], 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(self._students.values())[0].keys())

            writer.writeheader()
            writer.writerows(self._students.values())

        self.stdout.write(f"Finished: {timezone.now().isoformat()}")
        self.stdout.write(f"Duration: {timezone.now() - started_at}")

    def wake_up(self):
        self.stdout.write(self.style.WARNING("Waking up"))
        for student_email in self._students.keys():
            self.stdout.write(f"\t{self._students[student_email]['link']}", ending=': ')
            try:
                response = requests.head(self._students[student_email]['link'], timeout=1)
                self.stdout.write(str(response.status_code))
            except ReadTimeout:
                self.stdout.write("timeout")
            except BaseException:
                self.stdout.write("fail")

        self.stdout.write("Sleeping for a while")
        time.sleep(60)
