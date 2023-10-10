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