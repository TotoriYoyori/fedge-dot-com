# Configuration & Models ⚙️

Before we start the "3-Step Dance" 💃, we need to set up our "Stage" 🎭. This involves configuring our environment and defining how we store our keys in the database.

---

## 1. Package Structure 📂

Each part of the Google module has a dedicated home:

*   **`auth.py`**: The "Low-Level" OAuth magic (exchanging codes for tokens).
*   **`config.py`**: Environment settings (Client ID, Secret, Scopes).
*   **`models.py`**: Database tables (State and Credentials).
*   **`router.py`**: The "Entrypoints" for the browser (Login, Callback, Inbox).
*   **`service.py`**: The "Brain" (DB operations and calling Gmail).
*   **`credentials.json`**: The secret JSON file provided by Google.

---

## 2. Configuration ⚡

Our settings live in `src/config.py`. Here are the most important ones:

```python
GOOGLE_REDIRECT_URI: str # e.g., http://localhost:8000/google/callback
GOOGLE_SCOPES: str       # e.g., "openid email https://www.googleapis.com/auth/gmail.readonly"
```

**⚠️ The Golden Rule**: The `REDIRECT_URI` you put here **must match exactly** what you have configured in the [Google Cloud Console](https://console.cloud.google.com/). Even a missing `/` at the end will break the flow! 🛑

---

## 3. Data Models 💾

We have two types of data to store:

### 📥 `GoogleOAuthState` (Temporary)
This table acts as a **Waiting Room** 🛋️ for an in-progress login.

*   `state`: The unique string Google will send back.
*   `app_user_id`: Which user started this flow.
*   `code_verifier`: Our secret PKCE string.

*Once the user finishes logging in, we **delete** this row. It's one-time use!* 🧹

### 🔑 `GoogleOAuthCredential` (Durable)
This table is our **Safety Deposit Box** 🔒 for a user's keys.

*   `access_token`: The short-lived key.
*   `refresh_token`: The long-lived key.
*   `expiry`: When the access token dies.
*   `email_address`: The Gmail address of the connected account.

*This record is how we keep talking to Gmail long after the user has left our site.* 🏨

---

## 4. Why store tokens in a DB? 🤔

By saving the `refresh_token`, FEDGE can work in the background. Imagine if your phone asked for your password every time it checked for new emails—you'd throw it out the window! 📱💥

Our database lets us ask Google for fresh "Access Tokens" automatically, ensuring a seamless experience for our users.

**Nier Automata.** 🤖✨
