# GitHub Secrets Setup

Add these repository secrets in GitHub:

- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_CLIENT_ID`
- `FIREBASE_AUTH_URI`
- `FIREBASE_TOKEN_URI`
- `FIREBASE_AUTH_PROVIDER_CERT_URL`
- `FIREBASE_CLIENT_CERT_URL`

How to add them:

1. Open the repository on GitHub.
2. Go to `Settings` -> `Secrets and variables` -> `Actions`.
3. Click `New repository secret`.
4. Add each Firebase value as its matching GitHub secret.

Notes:

- Put the full private key into `FIREBASE_PRIVATE_KEY`.
- Keep the line breaks exactly as they appear in the service account key.
- The workflow at `.github/workflows/firebase-secrets-check.yml` rebuilds `.streamlit/secrets.toml` during CI and validates that the required values are present.
- File uploads are stored locally in `streamlit_uploads/`, so a Firebase Storage bucket is no longer required for this app.
- This helps for GitHub Actions, but Streamlit Cloud still needs its own app secrets if the app is hosted there.
