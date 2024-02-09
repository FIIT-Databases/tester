from crontab import CronTab
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Setup CRON jobs"

    def handle(self, *args, **options):
        self._cron()

    def _cron(self):
        cron = CronTab(user="root")
        cron.remove_all()

        for command, schedule in settings.CRON_JOBS.items():
            job = cron.new(command="cd /usr/src/app && python3 manage.py {}".format(command), comment=command)
            job.setall(schedule)
            job.enable()

        cron.write()
