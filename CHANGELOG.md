# Changelog

## 1.11.0 : 2024-02-10

- **Added**: [Save and prefill image on new test #5](https://github.com/FIIT-Databases/tester/issues/5)
- **Added**: Cool FIIT favicon (super important)
- **Added**: Advanced admin filters
- **Added**: [Basic job history](https://github.com/FIIT-Databases/tester/issues/3)
- **Added**: Creator in Evaluation
- **Added**: [Show request method #4](https://github.com/FIIT-Databases/tester/issues/4)
- **Changed**: Evaluations are managed from Django admin now
- **Changed**: Major task record logging refactor (messages introduced)
- **Changed**: Django 5.0 upgrade
- **Changed**: Use Debian-based containers

## 1.10.0 : 2023-05-16

- **Changed**: Alpine Linux 3.18
- **Fixed**: Build evaluation results keys using `set` manually

## 1.9.5 : 2023-05-06

- **Fixed**: Do not check for the response payload with HTTP 204 is returned

## 1.9.4 : 2023-05-05

- **Changed**: Extended timeouts

## 1.9.3 : 2023-05-02

```
Hate springs eternal
In this black heart of mine
Time heals nothing, I'll never forgive
Hate springs eternal
In this black heart of mine
Time heals nothing, I'll never forgive, never forget
Never ever
```

- **Fixed**: Bullshit response resolver using `TypeError` catch 🤷‍♂️

## 1.9.2 : 2023-05-02

- **Fixed**: Catch `docker.errors.ImageNotFound` in `client.images.get(self._task.image).remove(force=True)`

## 1.9.1 : 2023-05-02

- **Fixed**: Force image removal

## 1.9.0 : 2023-04-28

- **Added**: Scenario priority

## 1.8.1 : 2023-04-28

- **Fixed**: INVALID_HTTP_STATUS is now working

## 1.8.0 : 2023-04-26

- **Added**: Status code validation
- **Added**: Ignored properties in diff
- **Fixed**: Broader exception handling in the test execution (should prevent zombie stacking)

## 1.7.4 : 2023-04-05

- **Fixed**: Security for evaluations
- **Fixed**: Safely get additional info from tests

## 1.7.3 : 2023-03-17

- **Fixed**: requests timeout extended (to 10s)
- **Fixed**: nginx timeout extended

## 1.7.2 : 2023-03-17

- **Fixed**: Gunicorn timeout extended
- **Fixed**: Fixed a plethora of peculiar issues - honestly, I've already forgotten the specifics, but I'm too lazy to
dig through Git. Just know that the code is now as smooth as a ninja cat on roller skates!

## 1.7.1 : 2023-03-06

- **Fixed**: Disabled retry objects (because of the weird loops)

## 1.7.0 : 2023-03-03

- **Added**: Database schemas support

## 1.6.0 : 2023-02-27

- **Added**: **Evaluation** introduced
- **Fixed**: Private scenarios are executed only by `is_staff` users

## 1.5.1 : 2023-02-17

- **Fixed**: [Support for uppercase docker image name](https://github.com/FIIT-Databases/tester/issues/1)

## 1.5.0 : 2023-02-16

- **Added**: Capture Docker exceptions in Sentry
- **Fixed**: Execute clean-up every 5 minutes

## 1.4.2 : 2023-02-16

- **Fixed**: Forcing Docker image cleanup

## 1.4.1 : 2023-02-15

- **Changed**: Sleep time after container start raised to 5 seconds

## 1.4.0 : 2023-02-15

- **Added**: Usage of the `HTTPAdapter` with `Retry` object for better TCP retries

## 1.3.0 : 2023-02-14

- **Changed**: Phased job execution for better cleanups (implementation `BasicJob`)
- **Changed**: Prune docker images once per day

## 1.2.1 : 2023-02-11

- **Fixed**: Requirements for container

## 1.2.0 : 2023-02-11

- **Added**: Status endpoint `GET /api/v1/status`

## 1.1.0 : 2023-02-11

- **Added**: Nice footer
- **Added**: Create sandbox database users
- **Fixed**: Top users order
- **Fixed**: Version context processor

## 1.0.0 : 2023-02-11

- **Added**: LDAP auth
- **Added**: Ability to create scenarios with HTTP body
- **Added**: CRON
- **Added**: Database sandboxes
- **Changed**: Alpine Linux 1.17 container
- **Changed**: Docker containers runtime
- **Changed**: Removed CAPTCHA

## 0.4.1 : 2022-05-17

- **Changed**: Extended default request timeout to 20s

## 0.4.0 : 2022-03-23

- **Changed**: Assigment evaluation now has public link
- **Changed**: Administrator can execute private scenarios
- **Added**: Fancy charts (pimp my SVG ride)

## 0.3.0 : 2022-03-14

- **Added**: Introduced `Task.Status.FAILED` state which represents failed or time-outed `Task`
- **Added**: Public changelog
- **Added**: Instead of the HTML table a diff file is created if there is a large scenario payload

## 0.2.0 : 2022-03-09

- **Added**: Assigment evaluation management command
- **Changed**: `WEB` or `JOB` tasks

## 0.1.1 : 2022-02-24

- **Fixed**: Catching JSONDecodeError if there is an invalid JSON response provided

## 0.1.0

Initial
