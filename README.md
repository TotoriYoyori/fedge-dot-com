# FastAPI Scalable Monolithic Project Structure, the Guide

## (Update v0.1)
* Writing my first entry

****
## `.env`
Describe what variables, informations, keys, credentials that the program relies on to run. The same variable will vary per environment, preparing your apps to run differently depending on your computer, or on the cloud. 

**NEVER MAKE PUBLIC YOUR .ENV KEY IN THE CODEBASE**

| Type of `.env`       | Applicable to                                    | Example                                      |
|---------------------|-------------------------------------------------|---------------------------------------------|
| Local `.env`         | Information that your computer has; never share with others. | `DATABASE_URL=sqlite:///dev.db` <br> `SECRET_KEY=my-local-secret` |
| Deployment `.env`    | Information that the deployment server will have. | `DATABASE_URL=postgres://user:pass@db:5432/prod` <br> `SECRET_KEY=super-secret-value` |

****
## `/requirements`
`/requirements` folder can have multiple files to organize different requirements **per environments** for your project.

| File Name   | Applicable Environment                   | Example                                             |
|------------|-----------------------------------------|----------------------------------------------------|
| `base.txt` | For all environments                     | `fastapi`, `pydantic`, `SQLAlchemy`, `uvicorn`   |
| `dev.txt`  | Development, local, or staging          | `black`, `pytest`, `PrettyTable`                  |
| `prod.txt` | Production                               | `something`                                       |

****
## `/src`
### 1. App Entry Points and Setup
Create the following files in your `/src`:

| File Name       | Purpose                                                                                     | Important Snippet                          |
|-----------------|---------------------------------------------------------------------------------------------|-------------------------------------------|
| `__init__.py`   | Indicate to Python that `src` is a package and make public functions available.             | `__all__ = []`                            |
| `main.py`       | Entry point: initiate database, backend app, install middleware, and hook up configurations and environments. | `app = FastAPI()`      |
| `config.py`     | Read from environment variables and set up app configurations.                               | `class Config()`, `settings = Config()`   |
| `database.py`   | Session factory pattern and database engine initialization.                                  | `get_db()`, `engine = create_engine()`    |
| `exceptions.py` | Custom general exceptions.                                                                  | `MyException = HTTPException()`           |


### 2. One Package per Resource
Each package is a resource organizer. It groups routes, services, models, schemas, constants related to the delivery of an entity. When you need to introduce new resources to your API, you would also create a new folder.

*Example*: `/src/users` --> API routes related to delivering `users` data.

*Example*: `/src/orders` --> API routes related to delivering `orders` data.

### 3. Separate API logics into modules
Each API resources will mostly share the following architecture from **input (user's requests)** to **output (server's response)**.
1. First, the user makes a requests by HTTPs to our servers (e.g. `http://mywebsite.com/api/v1/resources`)
2. The requests is captured by a Web Server Gateway Interface, and routed to the server (because otherwise our server doesn't actually know how to parse https)
3. The requests URL is matched to one specified in `router.py`, which is like a map that points toward the correct response.
4. The router processes any dependency before performing the requests, in `dependencies.py`
4. The router will orchestrate a response model, according to one specified by your `schema.py`.
5. The router calls the service layer `service.py` to query and perform operations in the database.
6. The service layer maps and returns Python object in the form of ORM mapping of the database records. specified by your `models.py`
7. The information propagate upward to route, encapsulated in a a response model, and return to the user.

| File Name         | Purpose                                                                                     | Important Snippet                                  |
|------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------|
| `__init__.py`     | Indicate to Python that this resource is a Python package.                                   | `__all__ = []`                                    |
| `router.py`       | Entry point. Resolve dependencies. Map user requests to the correct service and respond in the correct response model. | `@router.get('/', response_model=ResponseModel)` |
| `service.py`      | Perform DB operations and return ORM models.                                                | `def get_all_users(db) -> list[Users]`           |
| `schemas.py`      | Specify server's response format and perform field validation.                              | `class UserResponse:`, `class UserCreate:`      |
| `models.py`       | ORM models, allowing database records to be represented in Python as objects.              | `class User(Base):`                              |
| `dependencies.py` | Like `service.py`, but focused on validation and error-proofing.                            | `async def is_valid_id() -> bool`                |
| `exceptions.py`   | Customize exceptions to your business requirements.                                         | `class UserNotFound(HTTPException):`            |
| `constants.py`   | Declare constants for the entire resource.                                       | `PAGINATION_LIMIT = 10`            |
| `config.py`   | Customize per-resource configs.                                     | `class ResourceConfig(Config):`            |

****
## `/tests`
### 1. Create one test folder per route
Always prefix the resource folder you want to test with `test_` so that `pytest` knows how to find the test.

### 2. Create fixtures and write unit tests for each and every function
To make things easier on yourself and others, always use **dependency injection** patterns into your code so you can test the logic, without needing the result.
