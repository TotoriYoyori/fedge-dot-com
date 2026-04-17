# Talking to Gmail 📨

We have the keys! 🔑 Now let's see how we use them to fetch real data from Google.

---

## 1. The Workflow: `GET /google/inbox` 📥

When you hit our inbox endpoint, FEDGE performs a series of checks to ensure the connection is live and secure.

**Step-by-Step:**
1.  **Retrieve**: We load the **GoogleOAuthCredential** from the database for the current user.
2.  **Refresh (If Needed)**: We check if the `access_token` is expired. If it is, we use the `refresh_token` to get a shiny new one from Google. 🔄
3.  **Build**: We rebuild the Google `Credentials` object.
4.  **Connect**: We create a Gmail "Service" client.
5.  **Fetch**: We call Gmail to list the latest messages.

```python
# Simplified Inbox logic
record = await GoogleOAuthService.get_credential(db, user_id)
record = await refresh_credential_if_needed(db, record) # The "Auto-Refresher" 🔄
service = create_gmail_service(record)

results = service.users().messages().list(userId="me", maxResults=10).execute()
```

---

## 2. The "Auto-Refresher" 🔄🛡️

Access tokens are like **Temporary Entry Passes**—they die after about an hour. If we didn't have a refresh mechanism, the user would have to log in to Google every single hour!

Our `refresh_credential_if_needed` function is a background hero. It:
1.  Checks the clock. 🕰️
2.  Sees the token is about to expire.
3.  Asks Google for a new one.
4.  **Saves the new token** back to our database.

This keeps the engine running forever without human intervention! 🏎️💨

---

## 3. Extending the Inbox 🚀

The current endpoint only returns **IDs** and **Thread IDs**. If you want to read the full content (the "MIME" body), you would use the `get` method:

```python
# How to get one specific email
message = service.users().messages().get(
    userId="me",
    id=message_id,
    format="full"
).execute()
```

---

## Final Note 📝

Remember that we are currently requesting `gmail.readonly` permission. This means we can read, but we **cannot** delete, send, or move emails. If you need those powers, you'll need to update the **Scopes** in our configuration! 🔍

**Nier Automata.** 🤖✨
