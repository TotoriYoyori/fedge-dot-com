# Developer Exercises 🎓

Passive reading is good, but **Active Coding** is better! 💻 Use these exercises to prove you've mastered the Google OAuth flow in FEDGE.

---

## Exercise 1: Trace the Login 🕵️‍♂️
**Goal**: See the "Waiting Room" (DB) in action.

1.  Open your database tool (like SQLite Browser).
2.  Hit the endpoint: `GET /google/login?app_user_id=dev_test`.
3.  **STOP** before you click anything on the Google Consent page! ✋
4.  Refresh your `google_oauth_states` table. 
5.  **Verify**: Can you see your `app_user_id`, a random `state`, and a `code_verifier`?
6.  Finish the Google login.
7.  **Verify**: Is the row in `google_oauth_states` gone? Is there a new row in `google_oauth_credentials`?

---

## Exercise 2: The "Token Death" Test 🕰️💀
**Goal**: Verify that our "Auto-Refresher" actually works.

1.  Find your `access_token` in the `google_oauth_credentials` table.
2.  Manually edit the `expiry` date to be **1 hour in the past**. 💾
3.  Hit the inbox endpoint: `GET /google/inbox?app_user_id=dev_test`.
4.  **Verify**: Did the request still work? Check the database again—did the `access_token` and `expiry` change? If yes, the auto-refresher saved the day! 🦸‍♂️

---

## Exercise 3: Reproduce a Failure 💥
**Goal**: Learn to recognize the "Invalid State" error.

1.  Start a login: `GET /google/login?app_user_id=bad_test`.
2.  Copy the URL Google sends you to, but **don't go there yet**.
3.  Manually **delete** the state row from the `google_oauth_states` table. 🗑️
4.  Now, paste the URL and finish the Google login.
5.  **Verify**: You should get a `400 Bad Request` with "Invalid state parameter." Now you know what it looks like when the "Envelope" ✉️ is missing!

---

## Exercise 4: Add a New Feature 🚀
**Goal**: Call a new Google API endpoint.

1.  In `src/google/router.py`, add a new route: `GET /google/profile`.
2.  Use the `GoogleOAuthService` to get the credentials.
3.  Call the Gmail `getProfile` method:
    ```python
    profile = service.users().getProfile(userId="me").execute()
    ```
4.  Return the profile JSON.
5.  **Verify**: Can you see your Gmail storage limit and total message count? 📊

---

## Final Takeaway 🏆

You've now navigated the "OAuth 2.0 Jungle" 🌴. You know how to start a flow, handle the redirect, store the keys, and keep them fresh. 

Now, go forth and build something awesome! 

**Nier Automata.** 🤖✨
