import json
import logging
import os
import random
import string
import subprocess
import tempfile
from difflib import HtmlDiff
from json import JSONDecodeError
from time import sleep
from typing import Optional
from uuid import UUID

import docker
from django.conf import settings
from django.db import connection
from django.utils.translation import gettext as _
from docker.models.containers import Container
from requests import HTTPError, Timeout, Session, Request
from requests.exceptions import InvalidJSONError

from apps.core.models import Task, TaskRecord


def exception_handler(job, exc_type, exc_value, traceback):
    try:
        task = Task.objects.get(pk=job.args[0])
    except Task.DoesNotExist:
        return

    task.status = Task.Status.FAILED
    task.message = str(exc_value)
    task.save()


def basic(task_id: UUID, public_only: bool) -> Optional[Task]:
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        logging.error("Task %s does not exist!", task_id)
        return None

    if task.status != Task.Status.PENDING:
        logging.warning("Task %s is already done! Skipping.", task.pk)
        return None

    database = None
    if task.assigment.database:
        database = ''.join(random.choices(string.ascii_letters, k=10))
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {database} TEMPLATE {task.assigment.database};")

    client = docker.from_env()  # FIXME: asi tazko

    params = {
        'image': task.image,
        'detach': True,
        'environment': {
            'NAME': 'Arthur',
            'DATABASE_HOST': settings.DATABASES['default']['HOST'],
            'DATABASE_PORT': settings.DATABASES['default']['PORT'],
            'DATABASE_NAME': settings.DATABASES['default']['NAME'],
            'DATABASE_USER': settings.DATABASES['default']['USER'],
            'DATABASE_PASSWORD': settings.DATABASES['default']['PASSWORD'],
        },
        'name': task.id,
        'privileged': False,
        'network': settings.DBS_DOCKER_NETWORK
    }

    if not os.getenv('DOCKER'):
        params['ports'] = {
            '8000/tcp': '9050'
        }

    container: Container = client.containers.run(**params)

    sleep(3)
    container.reload()

    conditions = {}
    if public_only:
        conditions['is_public'] = True

    for scenario in task.assigment.scenarios.filter(**conditions):
        logging.info("Executing scenario %s for the task %s", scenario.pk, task.pk)

        if os.getenv('DOCKER'):
            container_ip = container.attrs['NetworkSettings']['Networks'][settings.DBS_DOCKER_NETWORK]['IPAddress']
            url = f"http://{container_ip}:8000{scenario.url}"
        else:
            url = f"http://127.0.0.1:9050{scenario.url}"

        record = TaskRecord(
            task=task,
            scenario=scenario,
            url=url
        )

        s = Session()
        req = Request(
            method=scenario.method,
            url=record.url,
        )
        if scenario.body:
            req.json = scenario.body

        try:
            r = s.send(req.prepare(), timeout=settings.DBS_TESTER_TIMEOUT)
        except Timeout as e:
            record.status = TaskRecord.Status.TIMEOUT
            record.message = str(e)
            record.save()
            continue
        except BaseException as e:
            record.status = TaskRecord.Status.ERROR
            record.message = str(e)
            record.save()
            continue

        record.duration = r.elapsed

        try:
            r.raise_for_status()
        except HTTPError as e:
            record.response = r.content
            record.status = TaskRecord.Status.ERROR
            record.message = str(e)
            record.additional_data = {
                'status_code': r.status_code
            }
            record.save()
            continue

        try:
            response = r.json()
        except (InvalidJSONError, JSONDecodeError) as e:
            record.response = r.content
            record.status = TaskRecord.Status.INVALID_JSON
            record.message = str(e)
            record.save()
            continue

        record.response = json.dumps(response, sort_keys=True, indent=4)
        valid_response = json.dumps(scenario.response, sort_keys=True, indent=4)

        if record.response == valid_response:
            record.status = TaskRecord.Status.OK
        else:
            valid_lines = valid_response.splitlines(keepends=True)
            response_lines = record.response.splitlines(keepends=True)
            if len(valid_response) > settings.DBS_TESTER_DIFF_THRESHOLD:
                actual = tempfile.NamedTemporaryFile()
                actual.write(record.response.encode())

                expected = tempfile.NamedTemporaryFile()
                expected.write(valid_response.encode())

                record.diff_type = TaskRecord.DiffType.FILE
                sub = subprocess.run(['git', 'diff', '--no-index', expected.name, actual.name], stdout=subprocess.PIPE)
                record.diff = sub.stdout.decode()

                expected.close()
                actual.close()
            else:
                d = HtmlDiff()
                record.diff_type = TaskRecord.DiffType.HTML
                record.diff = d.make_table(
                    valid_lines,
                    response_lines,
                    fromdesc=_("Valid response"),
                    todesc=_("Your response"),
                )
            record.status = TaskRecord.Status.MISMATCH

        record.save()

    task.status = Task.Status.DONE
    task.output = container.logs().decode()
    task.save()

    # Cleanup
    container.stop()
    container.remove()
    if database:
        with connection.cursor() as cursor:
            cursor.execute(
                f"DROP DATABASE {database};"
            )

    return task
