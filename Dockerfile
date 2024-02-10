FROM python:3.12-slim as builder

# System setup
RUN apt update -y
RUN apt install -y libffi-dev build-essential libsasl2-dev libpq-dev libjpeg-dev libldap-dev libjpeg-dev nodejs npm

# https://github.com/python-ldap/python-ldap/issues/432
RUN echo 'INPUT ( libldap.so )' > /usr/lib/libldap_r.so

WORKDIR /usr/src/app

# Copy source
COPY . .

## Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Dependencies
RUN pip install --user gunicorn wheel --no-cache-dir
RUN pip install --user -r requirements.txt --no-cache-dir

# JavaScript
RUN npm i
RUN npm run build

FROM python:3.12-slim as base

# Dependencies
RUN apt update -y
RUN apt install -y postgresql-client libjpeg-tools argon2 tzdata ldap-utils docker.io

WORKDIR /usr/src/app

COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/src/app /usr/src/app
ENV PATH=/root/.local/bin:$PATH

RUN date -I > BUILD.txt

# Prepare virtual env
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV DOCKER=1

FROM base as server

RUN apt install -y supervisor curl nginx cron

# nginx
COPY conf/http.conf /etc/nginx/sites-available/tester-dbs.fiit.stuba.sk
COPY conf/nginx.conf /etc/nginx/nginx.conf
RUN ln -s /etc/nginx/sites-available/tester-dbs.fiit.stuba.sk /etc/nginx/sites-enabled/tester-dbs.fiit.stuba.sk
RUN rm -f /etc/nginx/sites-enabled/default

# supervisord
COPY conf/supervisor.conf /etc/supervisor/supervisord.conf

# Health check
HEALTHCHECK CMD curl --fail http://localhost:9000/api/v1/status || exit 1

# Execution
RUN chmod +x conf/server_entrypoint.sh
CMD ["conf/server_entrypoint.sh"]

FROM base as worker

RUN chmod +x conf/worker_entrypoint.sh
RUN chmod +x conf/worker_probe.sh

HEALTHCHECK CMD conf/worker_probe.sh

CMD ["conf/worker_entrypoint.sh"]
