# Changelog

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
