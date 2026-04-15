# --------------- TODAY
# DEVOPTIMIZE: Authentication Route
# TODO: Implement role hierarchy (all admins are users, users are lowest, etc.)
# TODO: Add role to JWT token encoding so users' role are checked by token.
# TODO: Re-register a few users to test different roles.
# TODO: Later on we will lock certain routes to having access token and being authorized. (e.g. register/login only if no JWT)
# TODO: With role registration, implement role registration across the API.

# DEVOPTIMIZE: Messaging Route
# TODO: Update email message template with updated banner and new content.

# DEVOPTIMIZE: Deployment
# TODO: Refactor and prep for Docker deployment.


# --------------- BACKLOG

# TODO: Extract a list of customers that has ordered, but HAVEN'T BOOKED to use this API on.
# TODO: Manually email to a few users who met above criteria.

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


# DEVOPTIMIZE: Database Migration
# TODO: Add TODO for how to set up Alembic for future (must do this yourself)
