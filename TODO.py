# --------------- TODAY
# DEVOPTIMIZE: Messaging Route
# TODO: Clean up messaging route, there are many unused functions (designer.py)
# TODO: Update email message template with updated banner and new content.
# TODO: Now, we will send email
# TODO: Ask mom to borrow gmail account to get app key for temporary SMTP.

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

# DEVOPTIMIZE: Authentication Route


# DEVOPTIMIZE: Database Migration
# TODO: Add TODO for how to set up Alembic for future (must do this yourself)
