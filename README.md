# TesterDBS

DBS tester application

## Install

### Docker

Pre-build Docker image is available on GitHub Container registry as

Repository contains working example of `docker-compose.yml` configured for development environment. You can use
similar configuration also for production usage.  The application image will be build from the source.

Setup steps (container name may differ):

1. Initialize containers `docker-compose up`
2. TBD

Server started on port 8000.

### From source

We use [poetry](https://python-poetry.org/) for dependency management and [PostgreSQL](https://www.postgresql.org/) 13
(10+ should be compatible) as a data storage (acquisition files are stored on the filesystem, not in the database).
To set up instance with demo database follow these simple steps:

1. Create python virtual environment (`python -m venv venv`)
2. Enter environment (`source venv/bin/activate`)
3. Install dependencies `poetry install`
4. Create `.env` file according `.env.example`
5. Execute migrations `python manage.py migrate`
6. Create superuser using `python manage.py createsuperuser`

## Database

This project requires PostgresSQL 10+ database server to run. Here is the EER diagram bellow.

![](docs/eer.png)

## Libraries

- [django-rq](https://github.com/rq/django-rq)

---
Made with ❤️ and ☕️ FIIT STU (c) 2022
