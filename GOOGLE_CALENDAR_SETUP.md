# Google Calendar API Setup Guide

This guide will help you set up Google Calendar API credentials for your AI Calendar Scheduling Bot.

## Prerequisites

- Google account
- Access to Google Cloud Console
- Python environment with required dependencies (already installed via requirements.txt)

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account

2. **Create a new project** (or select existing one)
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter project name: `calendar-scheduler-bot` (or your preferred name)
   - Click "Create"

## Step 2: Enable Google Calendar API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Enable Calendar API**
   - Search for "Google Calendar API"
   - Click on "Google Calendar API"
   - Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. **Go to OAuth consent screen**
   - In the left sidebar, click "APIs & Services" > "OAuth consent screen"

2. **Configure the consent screen**
   - Choose "External" user type (unless you have Google Workspace)
   - Click "Create"

3. **Fill in required information**
   - App name: `AI Calendar Scheduler`
   - User support email: Your email address
   - Developer contact information: Your email address
   - Click "Save and Continue"

4. **Scopes** (Step 2)
   - Click "Save and Continue" (no changes needed)

5. **Test users** (Step 3)
   - Add your email address as a test user
   - Click "Save and Continue"

6. **Summary** (Step 4)
   - Review and click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create OAuth client ID**
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop application"
   - Name: `Calendar Bot Desktop Client`
   - Click "Create"

3. **Download credentials**
   - Click "Download JSON" button
   - Save the file as `credentials.json` in your project root directory
   - **Important**: This file contains sensitive information, keep it secure!

## Step 5: Place Credentials File

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

## Step 6: Test the Setup

1. **Run your bot**
   ```bash
   python main.py
   ```

2. **First-time authentication**
   - When you first try to create a calendar event, a browser window will open
   - Sign in with your Google account
   - Grant permissions to access your calendar
   - The browser will show "The authentication flow has completed"
   - A `token.json` file will be created automatically for future use

## Important Security Notes

- ✅ `credentials.json` and `token.json` are already in `.gitignore`
- ✅ Never commit these files to version control
- ✅ Keep your credentials file secure and private
- ✅ Only share your project without the credentials files

## Troubleshooting

### Error: "credentials.json not found"
- Make sure you downloaded the credentials file from Google Cloud Console
- Verify the file is named exactly `credentials.json` (not `client_secret_xxx.json`)
- Ensure it's in the same directory as `main.py`

### Error: "Access blocked: This app's request is invalid"
- Make sure you've configured the OAuth consent screen
- Add your email as a test user
- Verify the OAuth client ID is for "Desktop application"

### Error: "The OAuth client was not found"
- Double-check that you enabled the Google Calendar API
- Ensure you're using the correct Google Cloud project
- Try creating new OAuth credentials

### Browser doesn't open for authentication
- Check if you're running in a headless environment
- Ensure port 0 (random port) is available for the local server
- Try running from a local machine with a browser

## Environment Variables (Optional)

You can also set up environment variables for additional configuration:

```bash
# .env file
GOOGLE_CALENDAR_TIMEZONE=Asia/Singapore  # Adjust to your timezone
GOOGLE_CALENDAR_DEFAULT_DURATION=60      # Default event duration in minutes
```

## Next Steps

Once setup is complete:
1. Your bot will automatically authenticate with Google Calendar
2. Calendar events will be created in your primary Google Calendar
3. Events include reminders (1 day before via email, 30 minutes before via popup)
4. You can customize the timezone and event duration in the code

## Support

If you encounter issues:
1. Check the console logs for specific error messages
2. Verify all steps in this guide were completed
3. Ensure your Google account has calendar access
4. Try creating a new OAuth client ID if problems persist 