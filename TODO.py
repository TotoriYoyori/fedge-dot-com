# DEVOPTIMIZE: Workflow from app to database
# TODO: E. App gets raw, email HTML from Google API everyday.
# TODO: E. App parse HTML from raw email and returns all necessary fields to .JSON format.
# TODO: E. App import .JSON format into Pandas DataFrame.
# TODO: T. App integrates orders from different dataframe into one very wide dataframe.
# TODO: T. App cleans this wide DataFrame, URNDAS_XSR
# TODO: L. App uses backend API to make post requests to server.
# TODO: L. Server ingests data from cleaned data to put into SQLite.
# DEVOPTIMIZE: Workflow from database to presentation
# TODO: BE. App has a webpage with frontend.
# TODO: FE. Frontend components make requests to database using backend API.
# TODO: FE. Frontend displays information on the webpage.


# FIXME: Continuing on Auth service, leaving at JWT tokens in src/auth/service.py

# TODO: Add TODO for how to set up Alembic for future.
# DONE: Migrate POST /dummies to /auth so now user creation lives in auth,
# DONE: Also migrate any required auth-related schemas and models from dummies to /auth
# TODO: Organize and reduce overlap between having auth and create users at the same time.
# TODO: Keep a god-level POST /dummies to play around with adding users as needed.


