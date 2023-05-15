FROM alpine:3.18 as builder

WORKDIR /root

# System setup
RUN apk update
RUN apk add --no-cache pkgconfig make musl-dev libffi-dev gcc python3 python3-dev postgresql-dev curl py3-pip jpeg-dev zlib-dev tzdata freetype-dev g++ openldap-dev nodejs npm

# https://github.com/python-ldap/python-ldap/issues/432
RUN echo 'INPUT ( libldap.so )' > /usr/lib/libldap_r.so

WORKDIR /usr/src/app

# Copy source
COPY . .

# Prepare virtual env
ENV VIRTUAL_ENV=/opt/venv
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Python Dependencies
RUN pip install gunicorn wheel --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

# JavaScript
RUN npm i
RUN npm run build

FROM alpine:3.18

WORKDIR /usr/src/app

RUN echo "1.10.0" > VERSION.txt
RUN date -I > BUILD.txt

# Dependencies
RUN apk add --no-cache python3 supervisor curl libpq postgresql-client jpeg zlib py3-argon2-cffi tzdata alpine-conf nginx freetype-dev jpeg-dev git libldap docker-cli
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/src/app /usr/src/app

# Prepare virtual env
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV DOCKER=1

# Configuration
RUN mkdir /var/run/gunicorn
COPY conf/supervisor.conf /etc/supervisord.conf
COPY conf/http.conf /etc/nginx/http.d/default.conf
COPY conf/nginx.conf /etc/nginx/nginx.conf

# Timezone setup
RUN setup-timezone -z Europe/Bratislava

# Health check
HEALTHCHECK CMD curl --fail http://localhost:9000/api/v1/status || exit 1

# Execution
RUN chmod +x conf/entrypoint.sh
CMD ["conf/entrypoint.sh"]
