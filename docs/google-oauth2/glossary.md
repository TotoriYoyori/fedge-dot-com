# OAuth Terminology 📖

OAuth 2.0 can feel like it's full of "alphabet soup" 🥣. Here are the key terms you need to know to understand how FEDGE talks to Google.

---

## The Essentials 🗝️

### 1. The "Flow" 🌊
A `flow` is the in-memory transaction object. It's like a **Temporary Assistant** 🤵 that handles a single login attempt. It builds the URL, generates the security codes, and handles the exchange of information.

### 2. Authorization Code 🎟️
The short-lived code Google gives the user after they say "Yes." It's like a **Claim Ticket**—it's not the actual prize (the tokens), but you use it to claim the prize at the counter.

### 3. Access Token 🔑
The actual key used to unlock the Gmail API. It's powerful but **short-lived** (usually expires in 1 hour). Think of it like a hotel key card that stops working at checkout time.

### 4. Refresh Token 🔄
This is the "Golden Key." 🥇 It's long-lived and allows FEDGE to ask Google for a *new* Access Token without bothering the user. As long as we have this, we can keep reading emails in the background!

---

## Security Concepts 🛡️

### 5. State 🕵️
A unique, one-time string we send to Google. Google sends it back exactly as-is. We use it to verify that the person coming back from Google is the *same* person we sent there. It prevents **Cross-Site Request Forgery (CSRF)**.

### 6. Scopes 🔍
Scopes define the "Boundary" 🚧 of our permissions. Instead of asking for "Everything," we ask for specific things like:
*   `gmail.readonly`: "I only want to read emails, not send or delete them."
*   `openid` / `email`: "I just want to know who you are."

### 7. Redirect URI ↪️
The specific URL on *our* server where Google should send the user after they finish. If this doesn't match the one registered in Google Cloud **exactly**, the whole thing fails.

---

## The Pro Stuff (PKCE) 🧠

### 8. PKCE (Proof Key for Code Exchange) 🛡️✨
pronounced "pixie." It's an extra layer of security.

*   **Code Verifier**: A secret random string we generate and hide in our database.
*   **Code Challenge**: A hashed version of that secret we send to Google.

When we exchange the code for tokens, we send the original **Verifier**. Google hashes it and checks if it matches the challenge. This proves that no one "stole" the redirect in the middle!

---

## App Integration 👥

### 9. `app_user_id` 🆔
This is **our** ID for the user in FEDGE. It's how we link a "Google Account" to a "FEDGE User."

---

## Summary Table 📊

| Term | Analogy | Duration |
| :--- | :--- | :--- |
| **Auth Code** | Claim Ticket 🎟️ | Seconds |
| **Access Token** | Hotel Key Card 🔑 | 1 Hour |
| **Refresh Token** | Master Key 🥇 | Months/Years |
| **State** | Secret Password 🕵️ | One-time use |

**Nier Automata.** 🤖✨
