# Google Integration Overview 📧

Welcome to the **Google Integration** module! 🚀 This part of FEDGE is the bridge between our backend and the vast world of Google APIs—specifically **Gmail**.

Think of this module as a "Digital Passport" 🛂. It handles the paperwork of asking users for permission, getting their official "stamp" (credentials), and storing that stamp so we can act on their behalf later.

---

## What are we building? 🏗️

Your app wants to read a user's Gmail inbox. Because emails are sensitive, Google won't just let us in. We have to perform a **"3-Step Dance"** 💃 called OAuth 2.0:

1.  **The Ask**: We send the user to a Google login page.
2.  **The Permission**: The user says "Yes, FEDGE can read my emails."
3.  **The Secret Handshake**: Google sends the user back to us with a special code. We exchange that code for a long-term **Credential**.

---

## The Actors 🎭

To understand the flow, meet the three characters in our story:

*   **👤 The User**: Sitting in their browser, wanting to connect their Gmail.
*   **⚙️ FEDGE Backend**: The coordinator. It starts the flow, remembers the user, and talks to Google.
*   **🏢 Google**: The gatekeeper. It verifies the user's identity and issues the "keys" (tokens).

---

## The Mental Model 🧠

Here is how the data moves through our system:

```text
Browser -> GET /google/login?app_user_id=123
Backend -> Prepare a "Secure Envelope" (State + PKCE) ✉️
Backend -> Redirect User to Google's Consent Page 🎢
User    -> Signs in and approves access ✅
Google  -> Redirects User back to /google/callback?code=...
Backend -> Verifies the Envelope 🕵️
Backend -> Exchanges code for permanent Keys (Tokens) 🔑
Backend -> Saves Keys for User 123 in the Database 💾
Backend -> Ready to read Gmail! 📨
```

---

## Where to go next? 🗺️

Ready to dive deeper? Follow the breadcrumbs below:

1.  **[OAuth Glossary](./glossary.md)**: Learn the "Secret Language" of tokens and scopes. 📖
2.  **[Setup & Config](./setup-config.md)**: How we configure Google and what our database looks like. ⚙️
3.  **[The OAuth Dance](./workflow.md)**: A line-by-line walkthrough of the Login and Callback. 💃
4.  **[Talking to Gmail](./gmail-integration.md)**: How we use stored keys to fetch real emails. 📨
5.  **[Troubleshooting](./maintenance.md)**: What to do when things go wrong. 🛠️
6.  **[Developer Exercises](./onboarding.md)**: Hands-on tasks to master the Google flow. 🎓

---

## Final Note 📝

This module is built to be **stateless and secure**. We never store user passwords—only the specific "tokens" Google gives us, which we can revoke at any time.

**Nier Automata.** 🤖✨
