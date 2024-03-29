import json
import logging
import os
import random
import string
from difflib import HtmlDiff
from json import JSONDecodeError
from time import sleep
from typing import Optional
from uuid import UUID

import docker
import psycopg
import sentry_sdk
from django.conf import settings
from django.db import connection
from django.utils.translation import gettext as _
from docker.errors import ImageNotFound
from docker.models.containers import Container
from requests import Timeout, Session, Request
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


class BasicJob:
    def __init__(self, task: Task, public_only: bool):
        self._task = task
        self._public_only = public_only
        self._database_name = "dbs_tmp_" + "".join(random.choices(string.ascii_letters, k=10)).lower()
        self._database_password = "".join(random.choices(string.ascii_letters, k=10)).lower()

    def prepare(self):
        # Create temporary user
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE USER {self._database_name} WITH CREATEDB ENCRYPTED PASSWORD '{self._database_password}';"
            )
            cursor.execute(f"GRANT CONNECT ON DATABASE {self._task.assigment.database} TO {self._database_name};")
            connection.commit()

        conn = psycopg.connect(
            host=settings.DATABASES["default"]["HOST"],
            dbname=self._task.assigment.database,
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
            port=settings.DATABASES["default"]["PORT"],
        )

        with conn.cursor() as cursor:
            cursor.execute(f"GRANT USAGE ON SCHEMA public TO {self._database_name};")
            cursor.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {self._database_name};")
            conn.commit()
        conn.close()

        self._task.additional_information["database"] = {"name": self._database_name}

        # Recover database
        # command = [settings.PSQL_PATH, self._database_name]

        # with open(f"{settings.DBS_DATABASES_PATH}/{self._task.assigment.database}.sql") as f:
        #     proc = subprocess.Popen(
        #         " ".join(command),
        #         shell=True,
        #         stdin=f,
        #         stdout=subprocess.DEVNULL,
        #         env={
        #             "PGPASSWORD": self._database_password,
        #             "PGUSER": self._database_name,
        #             "PGHOST": settings.DATABASES["default"]["HOST"],
        #         },
        #     )
        #     proc.wait()

    def run(self):
        client = docker.from_env()

        params = {
            "image": self._task.image,
            "detach": True,
            "environment": {
                "NAME": "Arthur",
                "DATABASE_HOST": settings.DATABASES["default"]["HOST"],
                # 'DATABASE_HOST': 'docker.for.mac.localhost',
                "DATABASE_PORT": settings.DATABASES["default"]["PORT"],
                "DATABASE_NAME": self._task.assigment.database,
                "DATABASE_USER": self._database_name,
                "DATABASE_PASSWORD": self._database_password,
            },
            "name": self._task.id,
            "privileged": False,
            "network": settings.DBS_DOCKER_NETWORK,
            "extra_hosts": {"host.docker.internal": "host-gateway", "docker.for.mac.localhost": "host-gateway"},
        }

        if not os.getenv("DOCKER"):
            params["ports"] = {"8000/tcp": "9050"}

        container: Container = client.containers.run(**params)
        sleep(15)
        container.reload()

        conditions = {}
        if self._public_only:
            conditions["is_public"] = True

        for scenario in self._task.assigment.scenarios.filter(**conditions).order_by("-priority"):
            logging.info("Executing scenario %s for the task %s", scenario.pk, self._task.pk)

            if os.getenv("DOCKER"):
                container_ip = container.attrs["NetworkSettings"]["Networks"][settings.DBS_DOCKER_NETWORK]["IPAddress"]
                url = f"http://{container_ip}:8000{scenario.url}"
            else:
                url = f"http://127.0.0.1:9050{scenario.url}"

            record = TaskRecord(task=self._task, scenario=scenario, url=url, status=TaskRecord.Status.OK)

            s = Session()
            # retry = Retry(connect=6, backoff_factor=2)
            # adapter = HTTPAdapter(max_retries=retry)
            # adapter = HTTPAdapter()
            # s.mount('http://', adapter)
            # s.mount('https://', adapter)
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
                record.messages.append(str(e))
                record.save()
                continue
            except BaseException as e:
                record.status = TaskRecord.Status.ERROR
                record.messages.append(str(e))
                record.save()
                continue

            record.duration = r.elapsed
            record.response = r.content

            if r.status_code != scenario.status_code:
                record.status = TaskRecord.Status.INVALID
                record.messages.append(
                    f"Invalid HTTP Status code (received={r.status_code}, expected={scenario.status_code})"
                )

            if r.content:
                try:
                    response = r.json()
                    try:
                        record.response = json.dumps(
                            {key: response[key] for key in response if key not in (scenario.ignored_properties or [])},
                            sort_keys=True,
                            indent=4,
                        )
                    except TypeError:
                        record.response = json.dumps(response, sort_keys=True, indent=4)

                    valid_response = json.dumps(scenario.response, sort_keys=True, indent=4)

                    if record.response != valid_response:
                        valid_lines = valid_response.splitlines(keepends=True)
                        response_lines = record.response.splitlines(keepends=True)
                        d = HtmlDiff()
                        record.diff_type = TaskRecord.DiffType.HTML
                        record.diff = d.make_table(
                            valid_lines,
                            response_lines,
                            fromdesc=_("Valid response"),
                            todesc=_("Your response"),
                        )
                        record.status = TaskRecord.Status.INVALID
                        record.messages.append(f"JSON Mismatch")
                except (InvalidJSONError, JSONDecodeError) as e:
                    record.status = TaskRecord.Status.INVALID
                    record.messages.append("Invalid JSON")
                    record.additional_data["exception"] = str(e)
                record.save()

        self._task.status = Task.Status.DONE
        self._task.output = container.logs().decode()
        self._task.save()

        # Cleanup
        container.stop(timeout=5)
        sleep(5)
        container.remove(force=True)
        try:
            client.images.get(self._task.image).remove(force=True)
        except ImageNotFound:
            pass

    def cleanup(self):
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {self._database_name};")
            cursor.execute(f"DROP USER IF EXISTS {self._database_name};")
            connection.commit()

    @staticmethod
    def execute(task_id: UUID, public_only: bool) -> Optional[Task]:
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            logging.error("Task %s does not exist!", task_id)
            return None

        if task.status != Task.Status.PENDING:
            logging.warning("Task %s is already done! Skipping.", task.pk)
            return None

        job = BasicJob(task, public_only)
        job.prepare()
        try:
            job.run()
        except (BaseException, Exception, TypeError) as e:
            task.status = Task.Status.FAILED
            task.message = str(e)
            task.save()

            with sentry_sdk.push_scope() as scope:
                scope.set_extra("task", task.pk)
                scope.set_extra("image", task.image)
                sentry_sdk.capture_exception(e)

        job.cleanup()

        return task


def basic_job(task_id: UUID, public_only: bool) -> Optional[Task]:
    return BasicJob.execute(task_id, public_only)
