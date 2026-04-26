# ANJLEE DIGITAL SERVICES

Streamlit application for a digital service cafe / document center.

## Current Features

- Customer upload desk with grouped pickup-code orders
- File-wise print settings for multi-file uploads
- Passport and custom photo sheet generation
- Manager queue with pending/completed tracking
- Customer status tracking by pickup code
- Rates editor for services and photo sizes
- Firebase-backed order/user metadata
- Local file storage under `streamlit_uploads/`

## Service Coverage

The app currently supports:

- Print / Xerox
- Photo print
- Aadhaar / PAN / Ayushman / Property / Udyam services
- Driving licence support
- Electricity bill payment
- Mobile recharge service
- Money transfer service
- Bike rental
- Car rental
- Lamination
- Typing / form fill
- Government exam form service

## Local Run

```powershell
cd C:\Users\nitin\Documents\Codex\2026-04-24\check-python-now\cafe_application
python -m streamlit run app.py
```

## Firebase

The app uses Firebase for metadata storage.

Required local secrets live in:

- `.streamlit/secrets.toml`

The app currently stores uploaded files locally, so Firebase Storage is not required for uploads.

## Google Authentication

Google login is already wired in code through `st.login("google")`, but OAuth still needs to be configured.

### Why this is needed

- Google must know which app is requesting sign-in
- The app needs a redirect URI so Google can return the user after login
- Test users must be allowlisted while the OAuth app is in testing mode

### What to configure later

1. Create or choose a Google Cloud project.
2. Open `APIs & Services` -> `OAuth consent screen`.
3. Create an `External` app.
4. Fill in:
   - app name
   - support email
   - developer contact email
5. Add test users.
   Recommended manager test user:
   - `nitin8251@gmail.com`
6. Open `APIs & Services` -> `Credentials`.
7. Create `OAuth client ID`.
8. Choose `Web application`.
9. Add redirect URIs:
   - local: `http://localhost:8501/oauth2callback`
   - deployed: `https://YOUR-APP-URL/oauth2callback`
10. Copy the Google `client_id` and `client_secret`.

### Streamlit secrets format for Google auth

Add this later to `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "put-a-random-long-secret-here"

[auth.google]
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

### Notes

- Manager login can use Google allowlisting and/or manager PIN
- If Google OAuth is still in testing mode, the login account must be added under test users
- Without this config, the app falls back to guest mode

## GitHub Secrets

See:

- [GITHUB_SECRETS_SETUP.md](C:\Users\nitin\Documents\Codex\2026-04-24\check-python-now\cafe_application\GITHUB_SECRETS_SETUP.md)
