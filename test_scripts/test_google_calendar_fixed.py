#!/usr/bin/env python3
"""
Test script for Google Calendar API credentials (Fixed OAuth Flow)
This script uses a fixed port to avoid redirect_uri_mismatch errors
"""

import os
import sys
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def test_authentication():
    """Test Google Calendar API authentication with fixed port"""
    print("🔐 Testing Google Calendar API Authentication...")
    print("=" * 50)
    
    credentials_file = 'credentials.json'
    token_file = 'token.json'
    
    # Check if credentials file exists
    if not os.path.exists(credentials_file):
        print(f"❌ ERROR: {credentials_file} not found!")
        print(f"   Please download your OAuth 2.0 credentials from Google Cloud Console")
        print(f"   and save them as '{credentials_file}' in this directory.")
        return None
    
    print(f"✅ Found credentials file: {credentials_file}")
    
    creds = None
    
    # Check if token.json exists (stored credentials)
    if os.path.exists(token_file):
        print(f"✅ Found existing token file: {token_file}")
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            print("✅ Loaded existing credentials")
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing token: {e}")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing expired credentials...")
                creds.refresh(Request())
                print("✅ Successfully refreshed credentials")
            except Exception as e:
                print(f"❌ Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            try:
                print("🌐 Starting OAuth flow with fixed port...")
                print("   A browser window will open for authentication")
                print("   Make sure you have added http://localhost:8080/ to your OAuth redirect URIs")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                
                # Use fixed port 8080 instead of random port
                creds = flow.run_local_server(port=8080, open_browser=True)
                print("✅ Successfully authenticated with Google Calendar")
            except Exception as e:
                print(f"❌ Error during OAuth flow: {e}")
                print("\n🔧 TROUBLESHOOTING:")
                print("   1. Make sure you've added http://localhost:8080/ to your OAuth redirect URIs")
                print("   2. Go to Google Cloud Console > APIs & Services > Credentials")
                print("   3. Edit your OAuth client and add these redirect URIs:")
                print("      - http://localhost:8080/")
                print("      - http://127.0.0.1:8080/")
                print("   4. Make sure your OAuth client type is 'Desktop application'")
                return None
        
        # Save the credentials for the next run
        try:
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            print(f"✅ Saved credentials to {token_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save credentials: {e}")
    
    return creds

def test_calendar_service(creds):
    """Test Google Calendar service initialization"""
    print("\n🔧 Testing Google Calendar Service...")
    print("=" * 50)
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        print("✅ Successfully initialized Google Calendar service")
        return service
    except Exception as e:
        print(f"❌ Error building Google Calendar service: {e}")
        return None

def test_calendar_access(service):
    """Test basic calendar access"""
    print("\n📅 Testing Calendar Access...")
    print("=" * 50)
    
    try:
        # Get the primary calendar
        calendar = service.calendars().get(calendarId='primary').execute()
        print(f"✅ Successfully accessed primary calendar")
        print(f"   Calendar name: {calendar.get('summary', 'Unknown')}")
        print(f"   Calendar ID: {calendar.get('id', 'Unknown')}")
        print(f"   Time zone: {calendar.get('timeZone', 'Unknown')}")
        return True
    except HttpError as e:
        print(f"❌ HTTP Error accessing calendar: {e}")
        return False
    except Exception as e:
        print(f"❌ Error accessing calendar: {e}")
        return False

def test_list_events(service):
    """Test listing recent events"""
    print("\n📋 Testing Event Listing...")
    print("=" * 50)
    
    try:
        # Get events from the past week
        now = datetime.utcnow()
        past_week = now - timedelta(days=7)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=past_week.isoformat() + 'Z',
            timeMax=now.isoformat() + 'Z',
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("✅ Successfully queried events (no events found in past week)")
        else:
            print(f"✅ Successfully queried events (found {len(events)} events)")
            print("   Recent events:")
            for event in events[:3]:  # Show first 3 events
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                print(f"   • {summary} - {start}")
        
        return True
    except HttpError as e:
        print(f"❌ HTTP Error listing events: {e}")
        return False
    except Exception as e:
        print(f"❌ Error listing events: {e}")
        return False

def test_create_test_event(service):
    """Test creating a test event"""
    print("\n🆕 Testing Event Creation...")
    print("=" * 50)
    
    try:
        # Create a test event for tomorrow
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)  # 2 PM tomorrow
        end_time = start_time + timedelta(hours=1)  # 1 hour duration
        
        event = {
            'summary': 'Google Calendar API Test Event',
            'description': 'This is a test event created by the Google Calendar API test script. You can safely delete this event.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Singapore',  # Adjust timezone as needed
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Singapore',  # Adjust timezone as needed
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        print("✅ Successfully created test event!")
        print(f"   Event ID: {created_event.get('id')}")
        print(f"   Event link: {created_event.get('htmlLink')}")
        print(f"   Event time: {start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   📝 Note: You can delete this test event from your calendar")
        
        return True, created_event.get('id')
    except HttpError as e:
        print(f"❌ HTTP Error creating event: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return False, None

def main():
    """Main test function"""
    print("🧪 Google Calendar API Credentials Test (Fixed OAuth)")
    print("=" * 60)
    print("This script will test your Google Calendar API setup")
    print("and verify that authentication and basic operations work.")
    print("\n⚠️  IMPORTANT: Make sure you've added http://localhost:8080/")
    print("   to your OAuth redirect URIs in Google Cloud Console!\n")
    
    # Test authentication
    creds = test_authentication()
    if not creds:
        print("\n❌ AUTHENTICATION FAILED")
        print("Please check the setup guide and OAuth redirect URIs.")
        return False
    
    # Test service initialization
    service = test_calendar_service(creds)
    if not service:
        print("\n❌ SERVICE INITIALIZATION FAILED")
        return False
    
    # Test calendar access
    if not test_calendar_access(service):
        print("\n❌ CALENDAR ACCESS FAILED")
        return False
    
    # Test listing events
    if not test_list_events(service):
        print("\n❌ EVENT LISTING FAILED")
        return False
    
    # Test creating an event
    create_success, event_id = test_create_test_event(service)
    if not create_success:
        print("\n❌ EVENT CREATION FAILED")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("✅ Your Google Calendar API credentials are working correctly!")
    print("✅ You can now use the calendar functionality in your bot.")
    print(f"✅ Test event created - you can delete it from your calendar")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1) 