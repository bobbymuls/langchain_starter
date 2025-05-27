#!/usr/bin/env python3
"""
Test script to verify the calendar functionality in main.py works
This tests the GoogleCalendarClient class from main.py directly
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the classes we need from main.py
from main import GoogleCalendarClient, IntentExtraction

async def test_main_calendar_integration():
    """Test the calendar integration from main.py"""
    print("🧪 Testing Calendar Integration from main.py")
    print("=" * 50)
    
    # Create a GoogleCalendarClient instance (same as in main.py)
    calendar_client = GoogleCalendarClient()
    
    # Test authentication
    print("🔐 Testing authentication...")
    auth_success = calendar_client.authenticate()
    
    if not auth_success:
        print("❌ Authentication failed!")
        return False
    
    print("✅ Authentication successful!")
    
    # Create a test intent (simulating what the bot would create)
    print("\n📅 Creating test intent...")
    
    # Create an intent for tomorrow at 3 PM
    tomorrow = datetime.now() + timedelta(days=1)
    test_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
    
    test_intent = IntentExtraction(
        activity="Test Meeting from Main Script",
        datetime_str=test_time.isoformat(),
        location="Singapore",
        confidence=0.9,
        is_weather_query=False,
        has_specific_time=True
    )
    
    print(f"✅ Test intent created:")
    print(f"   Activity: {test_intent.activity}")
    print(f"   Time: {test_intent.datetime_str}")
    print(f"   Location: {test_intent.location}")
    
    # Test event creation
    print("\n🆕 Testing event creation...")
    
    try:
        # This is the same method call that main.py uses
        success = await calendar_client.create_event(test_intent)
        
        if success:
            print("✅ Event created successfully!")
            print("   Check your Google Calendar for the new event")
            return True
        else:
            print("❌ Event creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during event creation: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Testing Main Script Calendar Integration")
    print("=" * 60)
    print("This will test the same calendar functionality used by your bot.\n")
    
    success = await test_main_calendar_integration()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("=" * 60)
        print("✅ Your main script's calendar integration is working!")
        print("✅ The bot will be able to create calendar events!")
        print("✅ Google Calendar API is properly integrated!")
    else:
        print("\n❌ FAILED!")
        print("=" * 60)
        print("❌ There's an issue with the calendar integration")
        print("❌ Check the error messages above")
    
    return success

if __name__ == "__main__":
    import asyncio
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1) 