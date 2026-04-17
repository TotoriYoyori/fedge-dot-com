# Setting up database

FastAPI, unlike Django, doesn't come "battery-included" when it comes to data management.
Therefore, we will use `SQLAlchemy` to simplify working between database and our Python code.

****

## Install SQLAlchemy to your project
Install `SQLAlchemy` and add to your project's `requirements.txt`
```
pip install sqlalchemy
```
****

## Create `database.py` in your project
`database.py` is responsible for two things in your projects:

1. Create metadata for Alembic migration to streamline autorevision of
your database schema.

2. Set up the `Base` class for your entire project's SQLAlchemy instance. This base 
class **will be inherited by all the models** in your project. 
```
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```




3. Create a global session factory `get_db` function t


