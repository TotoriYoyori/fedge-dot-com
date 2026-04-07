# Google Package

This package implements a backend OAuth 2.0 flow for Google so the server can:

1. Redirect a user to Google consent.
2. Receive the callback from Google.
3. Exchange the authorization code for OAuth credentials.
4. Store those credentials per app user.
5. Use the stored credentials to call the Gmail API.

This README is written for engineers who are new to backend OAuth. The goal is not just to tell you what the code does, but to explain why it is built this way and what can go wrong if you change it carelessly.

Primary source files for this package:

- [auth.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py)
- [config.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/config.py)
- [models.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py)
- [router.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py)
- [schemas.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/schemas.py)
- [service.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py)
- [main.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/main.py)

## What problem this package solves

Your app wants to read a user's Gmail inbox. That is sensitive data. Google will not let your backend read it unless:

- The user explicitly approves access.
- Google can identify your application.
- Your server can prove the callback belongs to an OAuth flow it started.
- Your server stores and reuses the credential issued for that specific user.

That sequence is OAuth.

## The mental model

There are three actors:

- The browser user.
- Your backend.
- Google.

The backend is the coordinator. It does not know the user's Gmail contents by default. It must first ask Google for permission on behalf of the user.

If you want to trace the orchestration entrypoints first, start with:

- [login()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L18)
- [callback()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L38)
- [list_inbox()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L93)

Think of the full flow like this:

```text
Browser -> GET /google/login?app_user_id=testuser
Backend -> Create Google OAuth flow + state + PKCE code_verifier
Backend -> Redirect browser to Google consent screen
Browser -> User signs in and approves access
Google -> Redirect browser back to /google/callback?code=...&state=...
Backend -> Validate state
Backend -> Exchange code for access token + refresh token + expiry + scopes
Backend -> Store credential for app_user_id
Backend -> Use credential to call Gmail API
```

## OAuth terms you must understand

## Glossary

### Flow

A `flow` is the in-memory OAuth helper object created by the Google library for one authorization attempt.

In this package, it is created by [get_google_flow()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py#L7).

It is responsible for things like:

- building the Google authorization URL
- generating the OAuth `state`
- generating the PKCE `code_verifier`
- exchanging the returned authorization `code` for credentials

It is not the same thing as:

- a FastAPI request
- a browser session
- a database record

It is best to think of it as the library's OAuth transaction object.

### Authorization code

The short-lived code Google sends to your callback after the user approves access.

The backend cannot use it directly for Gmail calls. It must exchange it for credentials.

### Access token

The token used to authenticate API calls to Google.

It is short-lived and usually expires.

### Refresh token

The longer-lived token used to obtain a new access token without sending the user through consent again.

This is what lets the backend keep working after the original access token expires.

### State

A one-time correlation and anti-CSRF value created by the backend before redirecting to Google.

In this package it is stored in [GoogleOAuthState](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L9) and validated in [callback()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L38).

Its job is to prove that the callback belongs to an OAuth flow this backend actually started.

### Scope

A permission string that tells Google what your app is asking to do.

Example:

```text
https://www.googleapis.com/auth/gmail.readonly
```

That means the app can read Gmail but not modify it.

### Redirect URI

The backend URL Google sends the browser back to after login and consent.

In this project the default is configured in [config.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/config.py).

### PKCE

PKCE is an extra protection layer for OAuth authorization code flows.

The short version:

- the backend generates a secret `code_verifier`
- Google sees only a derived challenge during the initial redirect
- the backend must send the original verifier during token exchange

If the backend loses the verifier, the code exchange fails.

### Code verifier

The original secret value used by PKCE.

In this package it is generated on login, stored with the temporary OAuth state, and restored on callback.

### Credential

In this package, a "credential" means the full reusable Google authorization data stored for a local app user.

That includes:

- access token
- refresh token
- token URI
- client ID
- client secret
- scopes
- expiry

This is stored in [GoogleOAuthCredential](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L19).

### `app_user_id`

This is your app's user identifier, not Google's.

Right now it is passed in the URL only because this project does not yet have a real app auth/session layer for deriving the current user automatically.

### Authorization code

This is the temporary code Google sends back to your callback URL after the user grants access.

- It is not the final token.
- It is short-lived.
- The backend exchanges it for real credentials.

### Access token

This is what the server uses to make authenticated API calls to Google.

- It expires.
- It is usually short-lived.

### Refresh token

This lets the backend ask Google for a new access token without sending the user through consent again.

- It is long-lived compared to the access token.
- It may not always be returned on every consent flow.
- This code requests offline access to get one.

### Scopes

Scopes define what the app is allowed to do.

Example:

```text
https://www.googleapis.com/auth/gmail.readonly
```

That means the app can read Gmail, but not modify it.

### Redirect URI

This is the backend URL Google redirects back to after login.

For this project the default is:

```text
http://localhost:8000/google/callback
```

This must match the redirect URI configured in Google Cloud exactly.

### State

`state` is an anti-CSRF value.

The backend creates it before redirecting to Google. Google sends it back unchanged. The backend uses it to verify:

- This callback belongs to a real OAuth flow it started.
- This callback maps back to the correct local app user.

If `state` is missing or wrong, the callback must be rejected.

### PKCE and code verifier

This is the part many juniors miss.

The Google OAuth library uses PKCE in this flow. PKCE adds a `code_verifier` and a derived challenge to the authorization request. When the backend later exchanges the returned authorization code, it must send the original `code_verifier` too.

If the backend loses that value, Google rejects the token exchange.

That is why this package stores `code_verifier` in the database along with `state`.

Without that, you get errors like:

```text
oauthlib.oauth2.rfc6749.errors.InvalidGrantError: (invalid_grant) Missing code verifier.
```

## Why the backend stores state and credentials

There are two different storage concerns in this package.

### Temporary OAuth state

Stored in `google_oauth_states`.

Implementation:

- [GoogleOAuthState](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L9)
- [GoogleOAuthService.create_state()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L12)
- [GoogleOAuthService.consume_state()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L28)

Purpose:

- Keep the OAuth `state`.
- Keep the app user ID that started the flow.
- Keep the PKCE `code_verifier`.

This row is temporary and is deleted after the callback is consumed.

### Long-lived Google credential

Stored in `google_oauth_credentials`.

Implementation:

- [GoogleOAuthCredential](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L19)
- [GoogleOAuthService.upsert_credential()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L52)
- [GoogleOAuthService.get_credential()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L45)

Purpose:

- Persist per-user access tokens.
- Persist refresh tokens.
- Persist scopes, expiry, and profile email.
- Rebuild a Google `Credentials` object later.

This row is the durable link between your app user and their Google authorization.

## Package structure

```text
src/google/
  auth.py       -> creates OAuth flow and exchanges code for credentials
  config.py     -> Google-specific env/config values
  models.py     -> SQLAlchemy tables for state and credentials
  router.py     -> FastAPI endpoints
  schemas.py    -> response schemas
  service.py    -> DB operations and Gmail service construction
  credentials.json -> Google OAuth client secret JSON
```

## Configuration

Configuration lives in `config.py`.

Source:

- [config.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/config.py)
- [get_google_flow()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py#L7)

The key values are:

```python
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/google/callback",
)

GOOGLE_SCOPES = [
    "openid",
    "email",
    "https://www.googleapis.com/auth/gmail.readonly",
]
```

Important notes:

- `openid` and `email` are included so the backend can retrieve basic identity context.
- `gmail.readonly` is the Gmail permission currently requested.
- If you change scopes, users may need to re-consent.
- If you change the redirect URI, you must update Google Cloud too.

## Data model

### `GoogleOAuthState`

This table tracks an in-progress OAuth login.

Source:

- [GoogleOAuthState](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L9)

```python
class GoogleOAuthState(Base):
    state: str
    app_user_id: str
    code_verifier: str | None
    created_at: datetime
```

Field meaning:

- `state`: the anti-CSRF value returned by Google.
- `app_user_id`: your app's user identifier.
- `code_verifier`: the original PKCE verifier required during token exchange.
- `created_at`: useful for debugging and later cleanup jobs.

### `GoogleOAuthCredential`

This table stores the reusable Google credential for a user.

Source:

- [GoogleOAuthCredential](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L19)

```python
class GoogleOAuthCredential(Base):
    app_user_id: str
    access_token: str
    refresh_token: str | None
    token_uri: str
    client_id: str | None
    client_secret: str | None
    scopes: str
    expiry: datetime | None
    email_address: str | None
    created_at: datetime
    updated_at: datetime
```

Important design note:

- `app_user_id` is unique. This means one app user maps to one stored Google credential in the current design.

## Endpoint walkthrough

### 1. `GET /google/login`

This endpoint starts the OAuth flow.

Source:

- [login()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L18)
- [get_google_flow()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py#L7)

Input:

```text
/google/login?app_user_id=testuser
```

What it does:

1. Builds a Google OAuth flow object.
2. Asks the flow object for an authorization URL.
3. The library also generates:
   - `state`
   - PKCE `code_verifier`
4. Stores those values in the database.
5. Redirects the browser to Google.

Illustrative version:

```python
flow = get_google_flow()
auth_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    prompt="consent",
)

await GoogleOAuthService.create_state(
    db,
    state=state,
    app_user_id=app_user_id,
    code_verifier=flow.code_verifier,
)

return RedirectResponse(auth_url)
```

Why these flags matter:

- `access_type="offline"` asks for a refresh token.
- `prompt="consent"` forces the consent screen so Google is more likely to return a refresh token during development.
- `include_granted_scopes="true"` allows incremental authorization behavior.

### 2. `GET /google/callback`

This endpoint finishes the OAuth flow.

Source:

- [callback()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L38)
- [fetch_credentials_from_code()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py#L16)

Input from Google:

```text
/google/callback?code=...&state=...
```

What it does:

1. Looks up the stored `state`.
2. Rejects the request if the state is unknown.
3. Recreates the Google flow.
4. Restores the stored PKCE `code_verifier`.
5. Exchanges the authorization code for credentials.
6. Calls Gmail `users().getProfile(userId="me")` to discover the email address.
7. Stores or updates the credential for that app user.
8. Returns a summary payload.

Illustrative version:

```python
oauth_state = await GoogleOAuthService.consume_state(db, state)
if oauth_state is None:
    raise HTTPException(status_code=400, detail="Invalid state parameter")

flow = get_google_flow(state=state)
creds = fetch_credentials_from_code(
    flow,
    code,
    code_verifier=oauth_state.code_verifier,
)

record = await GoogleOAuthService.upsert_credential(
    db,
    app_user_id=oauth_state.app_user_id,
    credentials=creds,
    email_address=profile.get("emailAddress"),
)
```

Important behavior:

- `consume_state` deletes the state row after successful lookup.
- This makes the state single-use, which is what you want.

### 3. `GET /google/credential`

This is a debugging and inspection endpoint.

Source:

- [get_credential()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L76)

It does not return the raw access token. It returns a safe summary:

- app user ID
- email address
- scopes
- expiry

This is useful when onboarding or debugging.

### 4. `GET /google/inbox`

This endpoint uses the stored credential to call Gmail.

Source:

- [list_inbox()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L93)
- [create_gmail_service()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L126)
- [refresh_credential_if_needed()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L98)

Input:

```text
/google/inbox?app_user_id=testuser&max_results=10
```

What it does:

1. Loads the stored credential from the DB.
2. Rebuilds a Google `Credentials` object.
3. Refreshes the access token if needed.
4. Builds a Gmail service client.
5. Calls Gmail `messages().list(...)`.

Illustrative version:

```python
record = await GoogleOAuthService.get_credential(db, app_user_id)
record = await refresh_credential_if_needed(db, record)
service = create_gmail_service(record)

results = service.users().messages().list(
    userId="me",
    maxResults=max_results,
).execute()
```

## Service layer walkthrough

The service layer keeps router code small and centralizes DB behavior.

Source:

- [GoogleOAuthService](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L12)

### `create_state`

Creates a temporary state row before redirecting to Google.

Why this exists:

- the router should not contain raw DB object creation logic
- the package needs a single place to control what OAuth state means

### `consume_state`

Reads and deletes the state row.

Why deleting is correct:

- OAuth states should be one-time use
- reused states can be a security problem
- this prevents accidental replay of callbacks

### `upsert_credential`

Creates or updates a durable credential record.

Why upsert matters:

- the same app user may reconnect Google later
- token refreshes update token values and expiry
- profile email or scopes may change

### `build_credentials`

Converts the SQLAlchemy credential record back into a Google `Credentials` object.

That object is what the Google API client actually knows how to use.

### `refresh_credential_if_needed`

Checks if the access token is expired.

If expired and a refresh token exists, it calls:

```python
creds.refresh(Request())
```

Then it saves the updated token values back to the database.

This is a key backend concept:

- Your app should not ask the user to log in again every time an access token expires.
- That is exactly what refresh tokens are for.

### `create_gmail_service`

Builds the Gmail API client from stored credentials.

This separates "how we store a credential" from "how we call Gmail."

## Auth helper walkthrough

`auth.py` is intentionally small.

Source:

- [auth.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py)

### `get_google_flow`

Creates a Google `Flow` using:

- the client secret file
- configured scopes
- configured redirect URI

### `fetch_credentials_from_code`

This function performs the token exchange.

Important detail:

```python
if code_verifier:
    flow.code_verifier = code_verifier
flow.fetch_token(code=code)
```

This is what fixes the PKCE callback problem.

## Startup schema behavior

This package contains a compatibility helper:

```python
await ensure_google_oauth_schema(session)
```

Why it exists:

- `Base.metadata.create_all()` creates missing tables.
- It does not alter existing tables to add new columns.
- The project already had an existing SQLite DB.
- We added `code_verifier` later.

So `ensure_google_oauth_schema()` checks SQLite schema and runs:

```sql
ALTER TABLE google_oauth_states ADD COLUMN code_verifier TEXT
```

This is a pragmatic bridge, not a long-term migration strategy.

For production-grade schema evolution, use Alembic migrations instead.

Source:

- [ensure_google_oauth_schema()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L140)
- [lifespan()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/main.py#L15)

## How the package currently identifies a user

Right now the package uses:

```text
app_user_id
```

passed as a query parameter.

This is a deliberate simplification because the broader app does not yet have a real authentication/session layer wired into the Google flow.

In a more complete system:

- the user would already be logged into your app
- the backend would derive `app_user_id` from the session or JWT
- `/google/login` would not accept arbitrary user IDs from the URL

This is the biggest architectural simplification in the current implementation.

Do not confuse:

- "Google-authenticated user"
- "your app's authenticated user"

They are related, but not the same thing.

## Common failure modes

### 1. `Invalid state parameter`

Meaning:

- callback state was missing
- callback state was wrong
- state was already consumed
- app restarted and temporary in-progress state was lost before it was stored or before callback completed

Check:

- the row exists in `google_oauth_states`
- the callback URL contains the expected `state`

### 2. `Missing code verifier`

Meaning:

- PKCE was used, but the backend did not restore the original `code_verifier` at token exchange time

This package now stores it in `google_oauth_states.code_verifier`.

### 3. Refresh token is missing

Possible reasons:

- Google did not issue a refresh token on that consent run
- the user had already granted access previously
- consent behavior changed

During development, `prompt="consent"` helps.

### 4. Redirect URI mismatch

Meaning:

- Google Cloud configuration does not exactly match `GOOGLE_REDIRECT_URI`

This mismatch is very common.

### 5. Scope mismatch

Meaning:

- the app expects Gmail access but requested the wrong scopes
- or a user credential was created under an older set of scopes

### 6. Expired access token

Normally handled automatically by `refresh_credential_if_needed`.

If refresh also fails, inspect:

- whether a refresh token exists
- whether the stored client ID and secret are valid
- whether the Google app configuration changed

## Security notes

This package is a good local/dev learning implementation, but there are production concerns to improve.

### Sensitive data storage

Currently the DB stores:

- access token
- refresh token
- client secret

In a stronger production design, sensitive fields should be encrypted at rest.

### User identity

`app_user_id` from a query string is fine for learning, not for production.

In production, derive the local user identity from trusted app authentication.

### Cleanup

Temporary OAuth state rows should eventually be cleaned up if abandoned mid-flow.

Example:

- user starts login
- user never completes Google consent
- stale state row remains

This is not dangerous by itself, but cleanup is good hygiene.

### Scope minimization

Only request the scopes you truly need.

If you only need read access, keep `gmail.readonly`.

## How to extend this package safely

### If you want to read full message contents

The current inbox endpoint returns message IDs and thread IDs.

You can add another service call like:

```python
service.users().messages().get(
    userId="me",
    id=message_id,
    format="full",
).execute()
```

Be careful with:

- payload size
- MIME parsing
- privacy concerns

### If you want to send email

You need a broader Gmail scope, such as a send scope.

That means:

1. update `GOOGLE_SCOPES`
2. reconnect or re-consent users
3. handle Gmail send APIs

### If you want multiple Google accounts per app user

The current model makes `app_user_id` unique in `google_oauth_credentials`.

That means one Google credential per local user.

If you want multiple connected accounts, redesign around something like:

- credential ID
- provider account email
- provider subject ID
- a foreign key to the local app user

### If you want production-quality schema evolution

Replace the ad hoc schema compatibility helper with Alembic migrations.

## Recommended review sessions for juniors

If onboarding a junior team, I would teach this package in this order.

### Session 1: The protocol

Cover:

- what OAuth is
- what state is
- what scopes are
- what access and refresh tokens are
- what PKCE is

If they do not understand these words, code review will be shallow.

### Session 2: Trace one real request

Walk line by line through:

- `/google/login`
- Google redirect
- `/google/callback`
- `/google/inbox`

Ask them after each step:

- what data was created
- where it is stored
- why it is needed later

### Session 3: Data model and failure cases

Cover:

- why state is temporary
- why credentials are durable
- what happens when a token expires
- why `code_verifier` must survive the redirect

### Session 4: Safe changes

Have them implement a small feature like:

- fetch Gmail profile details
- return message snippets
- add a revoke endpoint

That is where understanding becomes operational.

## Exercise checklists

These are meant to turn passive understanding into maintainable engineering behavior.

### Exercise 1: Trace one login by hand

Goal:

- Understand exactly what gets created before redirect and what returns on callback.

Checklist:

- Call `GET /google/login?app_user_id=testuser`.
- Put a breakpoint or log in [login()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L18).
- Inspect the generated `auth_url`.
- Inspect the generated `state`.
- Inspect `flow.code_verifier`.
- Confirm a row was inserted into [GoogleOAuthState](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L9).
- Complete Google consent.
- Put a breakpoint or log in [callback()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L38).
- Verify the returned callback `state` matches the stored one.
- Verify the stored `code_verifier` is reused by [fetch_credentials_from_code()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/auth.py#L16).
- Verify the temporary state row is deleted afterward.
- Verify a row exists in [GoogleOAuthCredential](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L19).

Questions to answer afterward:

- Why is `state` temporary but the credential durable?
- Why can the backend not just use the `code` directly for Gmail calls?
- Why must the callback know the original `code_verifier`?

### Exercise 2: Follow one inbox request

Goal:

- Understand how stored credentials become live Gmail API calls.

Checklist:

- Call `GET /google/inbox?app_user_id=testuser&max_results=5`.
- Step through [list_inbox()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L93).
- Inspect the ORM credential loaded by [GoogleOAuthService.get_credential()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L45).
- Step through [build_credentials()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L86).
- Step through [refresh_credential_if_needed()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L98).
- Confirm whether a refresh actually happened.
- Step through [create_gmail_service()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L126).
- Inspect the Gmail API response shape.

Questions to answer afterward:

- What exact fields from the DB are needed to rebuild a Google credential?
- When would a refresh happen?
- What would fail if `refresh_token` were missing?

### Exercise 3: Reproduce and explain a failure

Goal:

- Learn the failure modes well enough to diagnose them quickly.

Checklist:

- Temporarily bypass `code_verifier` restoration in [callback()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py#L38).
- Re-run the flow and observe the error.
- Restore the code.
- Temporarily change `GOOGLE_REDIRECT_URI` to a mismatched value in [config.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/config.py).
- Observe the Google-side failure.
- Restore the config.
- Call the callback twice with the same `state`.
- Observe why single-use state matters.

Questions to answer afterward:

- Which failures happen before Google redirects back?
- Which failures happen during token exchange?
- Which failures happen only when calling Gmail later?

### Exercise 4: Add a safe feature

Goal:

- Make a small change without breaking the OAuth contract.

Suggested task:

- Add a new endpoint that returns Gmail profile details for a connected user.

Checklist:

- Reuse [GoogleOAuthService.get_credential()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L45).
- Reuse [refresh_credential_if_needed()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L98).
- Reuse [create_gmail_service()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L126).
- Add a response schema in [schemas.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/schemas.py).
- Add a router endpoint in [router.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/router.py).
- Add a focused test next to [test_google_oauth_api.py](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/tests/test_google/test_google_oauth_api.py).

Success criteria:

- No duplication of OAuth credential reconstruction logic.
- No raw token returned in the API response.
- The endpoint still works after the access token expires and refreshes.

### Exercise 5: Design review for production hardening

Goal:

- Move from “it works” to “it will survive real usage.”

Checklist:

- Identify where sensitive fields are stored in [GoogleOAuthCredential](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L19).
- Propose how to replace query-param `app_user_id` with app auth/session identity.
- Propose a cleanup strategy for abandoned rows in [GoogleOAuthState](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/models.py#L9).
- Propose replacing [ensure_google_oauth_schema()](/C:/Users/stanm/PycharmProjects/FedgeBackMVP/src/google/service.py#L140) with Alembic.
- Propose an encryption strategy for stored tokens.

Review output should answer:

- What is acceptable for local development only?
- What must change before production?
- Which change is security-critical vs convenience-only?

## Quick reference

### Start login

```text
GET /google/login?app_user_id=testuser
```

### Inspect stored credential summary

```text
GET /google/credential?app_user_id=testuser
```

### Read inbox

```text
GET /google/inbox?app_user_id=testuser&max_results=10
```

### Run focused tests

```powershell
.\.venv\Scripts\python -m pytest tests\test_google\test_google_oauth_api.py
```

## Final takeaway

This package is not just "redirect user to Google and save a token."

It is a stateful backend protocol with four core responsibilities:

1. Start an OAuth flow safely.
2. Survive the redirect with enough data to complete it.
3. Persist the resulting credential per local user.
4. Rebuild and refresh that credential later to call Gmail reliably.

If a future engineer keeps those four responsibilities intact, they can change the implementation confidently.
