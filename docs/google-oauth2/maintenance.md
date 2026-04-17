# Troubleshooting & Security 🛠️

Even the best dancers trip sometimes! 💃💥 Here is how to handle errors and keep our Google integration secure.

---

## 1. Common Failure Modes 🆘

### 🕵️ `Invalid state parameter`
*   **What it means**: The "Secure Envelope" ✉️ we expected back from Google is missing, wrong, or already used.
*   **Fix**: Ensure you aren't hitting the "Back" button in your browser. States are **one-time use**.

### 🧩 `Missing code verifier`
*   **What it means**: We used PKCE for security, but forgot the "Secret Word" 🤫 when we tried to claim our tokens.
*   **Fix**: Check if the `code_verifier` was saved correctly in the `google_oauth_states` table during login.

### 🔄 Missing Refresh Token
*   **What it means**: Google gave us a temporary key, but not the "Master Key."
*   **Fix**: This usually happens if the user has already granted access before. During development, we use `prompt="consent"` in the login URL to force Google to show the permission screen again.

### ↪️ Redirect URI Mismatch
*   **What it means**: Google sent the user to a place we didn't authorize. 🛑
*   **Fix**: Go to the Google Cloud Console and make sure the "Authorized redirect URIs" match `settings.GOOGLE_REDIRECT_URI` **character for character**.

---

## 2. Security Best Practices 🛡️

### 🔑 Sensitive Data
Right now, we store tokens (Access and Refresh) in plain text in the database.
*   **Pro Tip**: In a production environment, these should be **encrypted at rest**. If someone steals our database, we don't want them to have "Master Keys" to everyone's Gmail! 🔐

### 🆔 User Identity
Currently, we pass `app_user_id` as a query parameter.
*   **Caution**: This is for local development only. In production, we derive the user's identity from their **JWT Session Token** to prevent "Identity Spoofing." 👤🎭

### 🧹 Cleanup
Stale rows in the `google_oauth_states` table (from users who started logging in but changed their mind) should be cleaned up periodically. They are harmless, but it's good "Code Hygiene." 🧼

---

## 3. Extending Safely 🚀

If you want to add new Google features:
1.  **Scope Minimization**: Only ask for the permissions you *truly* need. Don't ask for "Full Gmail Access" if you only need to read snippets. 🔍
2.  **Reuse Logic**: Always use `refresh_credential_if_needed` before calling any Google API to avoid `401 Unauthorized` errors. 🔄

**Nier Automata.** 🤖✨
