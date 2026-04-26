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

## WhatsApp Integration Later

WhatsApp Business integration is feasible for this app, but it is intentionally deferred for a later phase.

### Planned flow

1. Customer sends a service keyword like `PAN card`, `PAN correction`, or `Aadhaar update` on WhatsApp.
2. A webhook receives the message and maps it to the same service catalog used by this app.
3. WhatsApp sends a guided questionnaire:
   - customer name
   - phone number
   - service option
   - required documents
   - notes
4. The customer uploads files or photos in chat.
5. The backend stores those files and creates the same order structure used by the Streamlit upload desk.
6. The manager sees the order in the existing queue with a pickup code.

### What will be needed

- Meta `WhatsApp Business Cloud API`
- Meta developer app and business verification
- One WhatsApp Business phone number
- Public webhook endpoint for incoming messages
- Conversation state storage per customer phone number
- Media download and local storage pipeline
- Integration layer that reuses the existing order creation flow

### Suggested project structure for later

- `api/whatsapp_webhook.py`
- `services/whatsapp_service.py`
- `services/whatsapp_flow.py`
- `services/whatsapp_state.py`

### Pricing note

As of `April 26, 2026`, WhatsApp Business Platform pricing is based on Meta message charges plus any provider markup if a BSP is used.

India reference rates captured for later planning:

- Marketing: about `Rs. 0.8631` per delivered message
- Utility: about `Rs. 0.1150` per delivered message
- Authentication: about `Rs. 0.1150` per delivered message
- Authentication International: about `Rs. 2.3000` where applicable

Official pricing reference:

- `https://developers.facebook.com/docs/whatsapp/pricing`

### Important note

- This should be built as a business workflow assistant for services and orders
- It should not be designed as a general-purpose AI chatbot inside WhatsApp
- The existing app service catalog should remain the source of truth for questionnaire steps

## GitHub Secrets

See:

- [GITHUB_SECRETS_SETUP.md](C:\Users\nitin\Documents\Codex\2026-04-24\check-python-now\cafe_application\GITHUB_SECRETS_SETUP.md)
