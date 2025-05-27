# Google Calendar API Setup Guide

This comprehensive guide will help you set up Google Calendar API credentials for your AI Calendar Scheduling Bot, including troubleshooting for common issues.

## 📋 Prerequisites

- Google account
- Access to Google Cloud Console
- Python environment with required dependencies (already installed via requirements.txt)

## 🚀 Quick Setup (Recommended)

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account

2. **Create a new project** (or select existing one)
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter project name: `calendar-scheduler-bot` (or your preferred name)
   - Click "Create"

### Step 2: Enable Google Calendar API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Enable Calendar API**
   - Search for "Google Calendar API"
   - Click on "Google Calendar API"
   - Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth consent screen**
   - In the left sidebar, click "APIs & Services" > "OAuth consent screen"

2. **Configure the consent screen**
   - Choose "External" user type (unless you have Google Workspace)
   - Click "Create"

3. **Fill in required information**
   - **App name**: `Personal Calendar Scheduler`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
   - Click "Save and Continue"

4. **Scopes** (Step 2)
   - Click "Save and Continue" (no changes needed)

5. **Test users** (Step 3)
   - **Click "Add Users"**
   - **Add your email address** (this is crucial!)
   - Click "Save and Continue"

6. **Summary** (Step 4)
   - Review and click "Back to Dashboard"

### Step 4: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create OAuth client ID**
   - Click "Create Credentials" > "OAuth client ID"
   - **Application type**: **"Desktop application"** (VERY IMPORTANT!)
   - **Name**: `Calendar Scheduler Desktop`
   - Click "Create"

3. **Download credentials**
   - Click "Download JSON" button
   - Save the file as `credentials.json` in your project root directory
   - **Important**: This file contains sensitive information, keep it secure!

### Step 5: Place Credentials File

1. **Move the downloaded file**
   - Rename the downloaded file to exactly `credentials.json`
   - Place it in your project root directory (same folder as `main.py`)

2. **Verify file structure**
   ```
   your-project/
   ├── main.py
   ├── credentials.json  ← Your downloaded credentials file
   ├── requirements.txt
   └── ...
   ```

### Step 6: Test the Setup

1. **Run your bot**
   ```bash
   python main.py
   ```

2. **First-time authentication**
   - When you first try to create a calendar event, a browser window will open
   - Sign in with your Google account
   - **Click "Advanced"** if you see a warning screen
   - **Click "Go to Personal Calendar Scheduler (unsafe)"**
   - **Click "Allow"** to grant permissions
   - The browser will show "The authentication flow has completed"
   - A `token.json` file will be created automatically for future use

## 🔧 Troubleshooting Common Issues

### Error: "credentials.json not found"
**Solution:**
- Make sure you downloaded the credentials file from Google Cloud Console
- Verify the file is named exactly `credentials.json` (not `client_secret_xxx.json`)
- Ensure it's in the same directory as `main.py`

### Error: "redirect_uri_mismatch"
**Symptoms:** Browser shows "Error 400: redirect_uri_mismatch"

**Solution:**
1. **Go to Google Cloud Console** > APIs & Services > Credentials
2. **Edit your OAuth client** (click the pencil icon)
3. **Add these redirect URIs**:
   ```
   http://localhost:8080/
   http://127.0.0.1:8080/
   ```
4. **Click "Save"**
5. **Try authentication again**

### Error: "Access blocked: This app's request is invalid"
**Symptoms:** OAuth consent screen shows access blocked

**Solution:**
1. **Check OAuth consent screen configuration**
2. **Make sure you added your email as a test user**
3. **Verify OAuth client type is "Desktop application"**
4. **Try creating new OAuth credentials if problem persists**

### Error: "Google hasn't verified this app"
**Symptoms:** Warning screen about unverified app

**Solution:**
This is normal for personal apps. Simply:
1. **Click "Advanced"** (bottom left of warning screen)
2. **Click "Go to [Your App Name] (unsafe)"**
3. **Click "Allow"** to grant permissions
4. **This is safe** - you're the developer of your own app

**Alternative:** Publish the app to remove warning:
1. Go to OAuth consent screen
2. Click "Publish App"
3. Click "Confirm"

### Error: "The OAuth client was not found"
**Solution:**
- Double-check that you enabled the Google Calendar API
- Ensure you're using the correct Google Cloud project
- Try creating new OAuth credentials
- Verify the `credentials.json` file is from the correct project

### Browser doesn't open for authentication
**Solution:**
- Check if you're running in a headless environment
- Ensure port 8080 is available for the local server
- Try running from a local machine with a browser
- Check firewall settings

### Error: "Token has been expired or revoked"
**Solution:**
1. **Delete the `token.json` file**
2. **Run the bot again** - it will re-authenticate
3. **Complete the OAuth flow** in the browser

## 🔄 Fresh Setup (If You Have Issues)

If you're experiencing persistent problems, start completely fresh:

### Step 1: Clean Slate
1. **Go to Google Cloud Console** > APIs & Services > Credentials
2. **Delete your current OAuth client**
3. **Go to OAuth consent screen** and reset if needed

### Step 2: Create New OAuth Setup
1. **Follow Steps 3-4 from Quick Setup above**
2. **Make sure to**:
   - Choose "External" user type
   - Add your email as test user
   - Select "Desktop application" type
   - Download credentials as `credentials.json`

### Step 3: Clear Local Files
1. **Delete old files**:
   ```bash
   rm credentials.json token.json  # Linux/Mac
   del credentials.json token.json  # Windows
   ```
2. **Place new `credentials.json`** in project root
3. **Run the bot** and complete OAuth flow

## 🛡️ Security Best Practices

### ✅ What's Already Secure
- `credentials.json` and `token.json` are in `.gitignore`
- OAuth 2.0 provides secure authentication
- Tokens are stored locally and refreshed automatically

### 🔒 Keep Your Setup Secure
- **Never commit** credential files to version control
- **Keep credentials file** secure and private
- **Only share your project** without the credential files
- **Regenerate credentials** if they're ever compromised

## 🎯 Environment Variables (Optional)

You can customize behavior with environment variables in your `.env` file:

```bash
# Optional calendar configuration
GOOGLE_CALENDAR_TIMEZONE=Asia/Singapore  # Adjust to your timezone
GOOGLE_CALENDAR_DEFAULT_DURATION=60      # Default event duration in minutes
```

## ✅ Verification Checklist

Before considering setup complete, verify:

- [ ] Google Cloud project created
- [ ] Google Calendar API enabled
- [ ] OAuth consent screen configured with your email as test user
- [ ] OAuth client created as "Desktop application"
- [ ] `credentials.json` downloaded and placed in project root
- [ ] Bot runs without credential errors
- [ ] OAuth flow completes successfully in browser
- [ ] `token.json` file created automatically
- [ ] Calendar events can be created (test with the bot)

## 🆘 Still Having Issues?

1. **Check the console logs** for specific error messages
2. **Verify all steps** in this guide were completed
3. **Try the Fresh Setup** process above
4. **Ensure your Google account** has calendar access
5. **Create a new OAuth client ID** if problems persist

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Bot starts without credential errors
- ✅ OAuth flow completes in browser
- ✅ `token.json` file is created
- ✅ Calendar events appear in your Google Calendar
- ✅ Subsequent bot runs don't require re-authentication

---

**Once setup is complete, your bot will automatically authenticate with Google Calendar and create real calendar events when users schedule activities!** 🚀 