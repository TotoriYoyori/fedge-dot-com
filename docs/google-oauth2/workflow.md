# The OAuth Dance 💃

Ready to see how the magic happens? 🪄 Let’s walk through the two main endpoints of our Google integration.

---

## 1. The Start: `GET /google/login` 🎢

This is where the user "Steps into the Flow" 🌊. It’s like getting in line for a roller coaster.

**What happens behind the scenes?**
1.  **Preparation**: FEDGE creates a "Flow" 🤵.
2.  **Security**: We generate a `state` (CSRF protection) and a `code_verifier` (PKCE).
3.  **Persistence**: We save these in our "Waiting Room" (DB) so we remember who started this ride.
4.  **Redirect**: We send the user’s browser to Google’s Consent Screen.

```python
# A look at our login logic (simplified)
flow = get_google_flow()
auth_url, state = flow.authorization_url(
    access_type="offline", # We want a Refresh Token! 🔄
    prompt="consent",      # Always ask for permission
)
await GoogleOAuthService.create_state(db, state, user_id, flow.code_verifier)
return RedirectResponse(auth_url)
```

---

## 2. The Return: `GET /google/callback` ↩️

This is where Google "Sends them Back" 🚪 after they say yes.

**What happens behind the scenes?**
1.  **Validation**: We check if the `state` Google sent back matches one in our Waiting Room. If not, we slam the door! 🚫🚪
2.  **Restore**: We pull the `code_verifier` (the PKCE secret) out of our database.
3.  **Exchange**: We give Google the `code` and our `code_verifier` and ask for the tokens.
4.  **Identity Check**: We call Gmail to ask, "Hey, what’s your email address?" 📧
5.  **Save & Cleanup**: We save the new **Credentials** and delete the temporary **State** record.

```python
# A look at our callback logic (simplified)
state_record = await GoogleOAuthService.consume_state(db, state) # Reads & Deletes 🧹
creds = fetch_credentials_from_code(flow, code, state_record.code_verifier)
record = await GoogleOAuthService.upsert_credential(db, user_id, creds, email)
```

---

## 🛠️ The PKCE "Gotcha" 🧩

Why do we save the `code_verifier` in the database?

Many developers forget this! The "Flow" object lives in the server's **RAM**. When we redirect the user to Google, the server "forgets" that specific object. When the user comes back to `/callback`, we have a *new* request and a *new* object.

By saving the `code_verifier` in our database, we can "rebuild" the original security state and prove to Google that we are the ones who started the flow! 🕵️✨

---

## What’s Next? 🏁

Now that we have the tokens saved in our database, we can actually talk to Gmail!

**[Talking to Gmail](./gmail-integration.md)**: See how we fetch your inbox! 📨

**Nier Automata.** 🤖✨
