# 🔐 Gmail OAuth Setup Guide

## 📋 Prerequisites
- Google Cloud Account
- Gmail account for expense tracking

---

## 🚀 Step-by-Step Setup

### 1️⃣ Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"**
3. Name: `SplitMint` (or your choice)
4. Click **"Create"**

### 2️⃣ Enable Gmail API

1. In your project, go to **APIs & Services** → **Library**
2. Search for **"Gmail API"**
3. Click on it and press **"Enable"**

### 3️⃣ Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure **OAuth consent screen**:
   - User Type: **External**
   - App name: `SplitMint`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add **Gmail API** (read-only)
   - Test users: Add your Gmail address
   - Click **Save and Continue**

4. Create OAuth Client:
   - Application type: **Desktop app**
   - Name: `SplitMint Desktop Client`
   - Click **Create**

5. **Download the JSON file**:
   - Click the **Download** button (⬇️ icon)
   - Save as `zyura_secret.json` in the `backend/` folder

### 4️⃣ Configure SplitMint

1. Copy the downloaded file to backend folder:
   ```bash
   # The file should be at:
   backend/zyura_secret.json
   ```

2. **Never commit this file!** (Already in `.gitignore`)

3. File structure should look like:
   ```json
   {
     "web": {
       "client_id": "YOUR_ID.apps.googleusercontent.com",
       "project_id": "your-project",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "YOUR_SECRET",
       "redirect_uris": ["http://localhost"]
     }
   }
   ```

### 5️⃣ First-Time Authentication

1. Run the setup script:
   ```bash
   cd backend
   python setup_gmail.py
   ```

2. Browser will open:
   - Sign in to your Gmail account
   - Click **"Allow"** to grant permissions
   - You may see "This app isn't verified" - click **"Advanced"** → **"Go to SplitMint (unsafe)"**
   - This is safe because it's YOUR app!

3. After authorization:
   - A `token.json` file will be created
   - This file stores your access token
   - **Keep this file secure!** (Also in `.gitignore`)

---

## 🔒 Security Best Practices

### ✅ DO:
- Keep `zyura_secret.json` and `token.json` **private**
- Add them to `.gitignore` (already done)
- Use OAuth for authentication (no passwords!)
- Revoke access if compromised: [Google Account → Security → Third-party apps](https://myaccount.google.com/permissions)

### ❌ DON'T:
- Commit secrets to Git
- Share your secret files
- Use production credentials for testing
- Hard-code API keys in code

---

## 🐛 Troubleshooting

### "File zyura_secret.json not found"
**Solution**: Download OAuth credentials from Google Cloud Console

### "Access blocked: Authorization Error"
**Solution**: 
1. Add your email to **Test users** in OAuth consent screen
2. Use the same Google account that owns the Cloud project

### "Invalid client"
**Solution**: Re-download credentials from Google Cloud Console

### "The app is requesting access to sensitive info"
**Solution**: This is normal for Gmail API. Click **"Advanced"** → **"Go to SplitMint"**

### "Token expired"
**Solution**: Delete `token.json` and run `setup_gmail.py` again

---

## 📚 More Information

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## 🔄 Revoking Access

To revoke SplitMint's access to your Gmail:

1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find **SplitMint**
3. Click **"Remove Access"**
4. Delete `token.json` from backend folder

---

**✅ Setup Complete!** You can now run SplitMint and it will automatically fetch transactions from your Gmail.
