# Mastering REST APIs with FastAPI

[Course hompage](https://www.udemy.com/course/rest-api-fastapi-python)


# Course Content

What is REST?
- client -server
- resource
    - posts, comments, likes, users
- stateless
    - server does not keep any information about the clients
    - in every request the client has to send all information needed to conclude the operation
- cacheable
    - a request can be saved in the cahce (without knowing from which client it is coming)
    - should be possible but not necessary
- uniform hypermedia-driven interface
    - confusing and more optional
    - tell client through which link the resource can be found
- if backend uses multiple servers, this should be invisible to client
    - e.g. one for posts and comments and another for authentication and registration
    - client does not see any backend slpits


# Working with FastAPI

Thought process:
1. What data does your API receive and return? (models)
2. What data do you need to store? (database)
3. Write the interface? (endpoints)

# Pytest

Using *Fixtures*: a couple of things to share between tests -> put in conftest.py in test folder.

Showing all defined fixtures: `pytest --fixtures`

Boundary Value Analysis: find out how many tests and which ones to write.

Run tests here with

```
docker compose run --rm backend sh -c "pytest"
```

## Test levels

Unit tests should not test third party libraries, but only the code you wrote yourself. So third party functions need to be mocked.
System tests should run less often, but cover the whole system - therefore third party libraries should be configured for that. Example: the file uploads to Backblaze B2: use a separate bucket for system tests.


# Async databases

Use asynchronous databases for FastAPI. Start with `encode/databases` module works with SQLAlchemy calls, so it can be exchanged later easily for SQLAlchemy + a real database.

Two ways to talk to a database:
- executing queries (used here through `encode/databases`)
- using an ORM

Compare to `SQLModel` which is a simple Object Relational Manager (ORM) for FastAPI and `SQLAlchemy` which is a comprehensive ORM for Python.

Whenever interacting with a database:
1. decide what to do
2. write the query
3. run the query

Ways of writing queries:
- SQLAlchemy's ORM
- companion ORM (python objects, as if they were connected to a database)
- using the database's module own query builder (e.g. `encode/databases`)
- using the database's own query language (e.g. SQL)

# Logging

- Loggers
- Handlers
- Formatters
- Filters

## Loggers, Handlers, and Formatters

In the realm of code, logging's a fickle dance,
Too many logs may leave budgets askance,
Find the right balance, and debug you can,
But log too much, you'll end up in a jam!
[ChatGPT]

Pros & Cons of loggers:
+ understand what happened at crashes
- can make code less readable
+ gain historical context of application
- need to pay for the storage of logs
+ Once setup, logging is easy
- confusing first time setting it up
+ Alerts and dashboards can be setup

Logging module in python:
`import logging`
logger (schedules log information for output)
-> handler (sends log information to destination)
-> formatter (formats log information)


## Example:
logger, 2 handlers (console handler, file handler), formatter (display current time + log message)


## Logging levels:
- Critical -> errors, that cause application failure, such as crucial database connection
- Error -> errors, that affect operation, such as an HTTP 500 error, but allow application to continue working
- Warning -> warnings, that do not affect operation, but may be important, such as a deprecated code usage or low disk space
- Info -> information about the application, such as a user authentication message or version info
- Debug -> information about the application, that is useful for debugging and testing


## Logging hierarchies
 using `__name__` to create a hierarchy of loggers: either set to string `"__main__"` (if called in main module) or the import path of the module (if called in another module).

Used for *logger inheritance*:
Example: app.routers.post uses first the loggers from `app.routers.post`, than passes the logs to the loggers of `app.routers`, and finally to the loggers of `app`.
If a logger is not found, it will look for the next logger in the hierarchy.
So, if loggers are configures on `app` level all imports will use those handlers, unless they are overwritten in the module itself.

`root` logger is above the `app` logger, so it will always be used, unless `propagate` is set to `False`.

## Logging filters

Loggers and handlers can each have filters.

Logging flow:
[Logging Flowchart](backend/doc/logging_flow.png)

## Cloud logging

Using [logtail](https://betterstack.com/logs) to send logs to a cloud logging service.

But use logtail only for production, not for development, for avoiding mixing up logs from different environments and cluttering production logs with development logs.

# Authentication

using *Jason Web Tokens* (JWT, also known as *Bearer* or *Access Token*) for authentication.

[JWT](doc/jwt.png)

JWT includes:
- header
    - type of token
    - hashing algorithm
- payload
    - data
    - expiration date
- signature

# Many-to-many relationships

Many-to-many relationships are super important, and fortunately not that complicated!

In this section we'll add "post likes".

To do this we'll follow our usual "new feature methodology":

- Decide what data we need to store (in `database.py`)
- Decide what data our API will receive as input and will return as output (in `models.py`)
- Implement the API endpoints to acquire and return the data (in `routers/post.py`)

We'll also introduce various new concepts, such as extracting queries to simplify re-using them, using Enum for sorting API responses, and using Pytest parametrization to simplify our tests.

# Email confirmation

Sending emails with FastAPI, include a link with secure_unique_token to confirm email address.
But the confirmation JWT needs to be different from the access token, otherwise user could copy and paste the token and use it as access token - without ever clicking at the confirm link.

Mailservices:
- Mailgun
- Mailgim
- Drip
- ActiveCampain
- ConvertKit

# Deploy

To [Render](https://www.render.com).

# PostrgeSQL

[ElephantSQL](https://www.elephantsql.com) offers more features in free tier than [Render](https://www.render.com).

database modifiation package: example: `alembic`