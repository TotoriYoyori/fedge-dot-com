# DEVOPTIMIZE: Messaging Route
# TODO: Set up project structure for message, have some placeholder route to make sure working.
# TODO: Accessing /notification/email to send emails to some guests
# TODO: /notification/email have access to some static HTML template for email sending.
# TODO: For now users can post freely to any email address to send them email
# TODO: Extract a list of customers that has ordered, but HAVEN'T BOOKED to use this API on.
# TODO: Later on, we will pull target email address from our database and backend google API.
# send_notify_email needs 1. a target email, 2. customer info, 3. template preset
# the user (mom) chooses a target_email
# target_email fetch customer_info
# customer_info inject into template
# route returns successful message
# customer info NEEDS a schema so returned user data fits this template preset



# DEVOPTIMIZE: Google Route
# TODO: E. App gets raw, email HTML from Google API everyday.
# TODO: E. App parse HTML from raw email and returns all necessary fields to .JSON format.
# TODO: E. App import .JSON format into Pandas DataFrame.
# TODO: T. App integrates orders from different dataframe into one very wide dataframe.
# TODO: T. App cleans this wide DataFrame, URNDAS_XSR
# TODO: L. App uses backend API to make post requests to server.
# TODO: L. Server ingests data from cleaned data to put into SQLite.
# TODO: Cleaned order has appropriate ORM model to interact with in Python.

# DEVOPTIMIZE: Frontend Integration
# TODO: Frontend register form to work with authentication/register
# TODO: Frontend login form to work with authentication/login
# TODO: Frontend makes a call to authentication/me to check credentials.

# DEVOPTIMIZE: Database Migration
# TODO: Add TODO for how to set up Alembic for future.

# DEVOPTIMIZE: Authentication Route
# TODO: Refactor /me route, it exposes a lot of functions atm in one route.

# DEVOPTIMIZE: Miscellaneous
