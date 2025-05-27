# Fresh Google Calendar OAuth Setup

Follow these steps to create a completely new OAuth setup that will work properly:

## Step 1: Clean Slate - Delete Current OAuth Client

1. **Go to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Navigate to**: APIs & Services > Credentials
3. **Find your current OAuth client** and **DELETE** it
4. **Also delete** any existing OAuth consent screen configuration

## Step 2: Create New OAuth Consent Screen

1. **Go to**: APIs & Services > OAuth consent screen
2. **Choose "External"** user type
3. **Fill in the form**:
   - **App name**: `Personal Calendar Scheduler`
   - **User support email**: `bobbymul93@gmail.com`
   - **Developer contact information**: `bobbymul93@gmail.com`
4. **Click "Save and Continue"**

5. **Scopes page**: Click "Save and Continue" (no changes needed)

6. **Test users page**:
   - **Click "Add Users"**
   - **Add**: `bobbymul93@gmail.com`
   - **Click "Save and Continue"**

7. **Summary page**: Click "Back to Dashboard"

## Step 3: Create New OAuth Client

1. **Go to**: APIs & Services > Credentials
2. **Click "Create Credentials" > "OAuth client ID"**
3. **Application type**: **Desktop application** (VERY IMPORTANT!)
4. **Name**: `Calendar Scheduler Desktop`
5. **Click "Create"**

## Step 4: Download New Credentials

1. **Click "Download JSON"** button
2. **Save as**: `credentials_new.json` in your project folder
3. **Backup your old file**: rename `credentials.json` to `credentials_old.json`
4. **Rename the new file**: `credentials_new.json` to `credentials.json`

## Step 5: Clear Old Tokens

1. **Delete**: `token.json` (if it exists)
2. **This forces a fresh authentication**

## Step 6: Test Again

Run the test script with the new credentials:
```bash
python test_google_calendar_fixed.py
```

## Why This Works

- **Desktop application** type automatically includes correct redirect URIs
- **Fresh OAuth consent screen** avoids verification issues
- **You're added as a test user** so you can access the app
- **Clean slate** removes any configuration conflicts

## If You Still Get Errors

1. **Make sure** you selected "Desktop application" (not Web application)
2. **Verify** your email is in the test users list
3. **Try** publishing the app instead of keeping it in testing mode
4. **Check** that Google Calendar API is enabled in your project 