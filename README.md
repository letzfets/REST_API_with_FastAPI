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

Boundary Value Analysis: find out how many tests and which ones to 

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