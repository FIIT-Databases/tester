import json
import logging
import subprocess
import tempfile
from difflib import HtmlDiff
from json import JSONDecodeError
from typing import Optional
from uuid import UUID

import docker
import requests
from django.conf import settings
from django.utils.translation import gettext as _
from docker.models.containers import Container
from requests import HTTPError, Timeout
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

    client = docker.from_env()  # FIXME: asi tazko
    container: Container = client.containers.run(
        image=task.image,
        detach=True,
        environment={
            'NAME': 'Arthur'
        },
        name=task.id,
        ports={
            '8000/tcp': '9050'
        },
        privileged=False
    )

    conditions = {}
    if public_only:
        conditions['is_public'] = True

    for scenario in task.assigment.scenarios.filter(**conditions):
        logging.info("Executing scenario %s for the task %s", scenario.pk, task.pk)

        record = TaskRecord(
            task=task,
            scenario=scenario,
            url=settings.DBS_TESTER_BASE_URL + scenario.url
        )

        try:
            r = requests.get(record.url, timeout=settings.DBS_TESTER_TIMEOUT)
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
    task.save()

    # Cleanup
    container.stop()
    container.remove()
    client.images.get(task.image).remove()

    return task
