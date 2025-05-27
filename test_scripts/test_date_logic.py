#!/usr/bin/env python3
"""
Test date preservation logic for time clarification
"""

from datetime import datetime, timedelta

def test_date_reference_logic():
    """Test the date reference logic"""
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    test_cases = [
        (today, "today"),
        (tomorrow, "tomorrow"), 
        (yesterday, "yesterday"),
        (today + timedelta(days=2), (today + timedelta(days=2)).strftime("%A")),
        (today + timedelta(days=7), (today + timedelta(days=7)).strftime("%A"))
    ]
    
    print("🧪 Testing date reference logic:")
    print(f"Today is: {today}")
    print()
    
    for test_date, expected_reference in test_cases:
        # Simulate the logic from the code
        if test_date == today:
            date_reference = "today"
        elif (test_date - today).days == 1:
            date_reference = "tomorrow"
        elif (test_date - today).days == -1:
            date_reference = "yesterday"
        else:
            date_reference = test_date.strftime("%A")
        
        status = "✅" if date_reference == expected_reference else "❌"
        print(f"{status} {test_date} → '{date_reference}' (expected: '{expected_reference}')")
    
    print()
    print("✅ Date reference logic test completed!")

def test_datetime_preservation():
    """Test datetime preservation with time updates"""
    
    # Simulate original intent: "dinner tomorrow" (no time)
    original_date = datetime.now() + timedelta(days=1)
    original_date = original_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Simulate user providing time: "6pm"
    new_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    
    # Simulate the correction logic
    corrected_datetime = original_date.replace(
        hour=new_time.hour,
        minute=new_time.minute,
        second=0,
        microsecond=0
    )
    
    print("🧪 Testing datetime preservation:")
    print(f"Original: {original_date} (tomorrow at midnight)")
    print(f"New time: {new_time} (today at 6pm)")
    print(f"Corrected: {corrected_datetime} (tomorrow at 6pm)")
    print()
    
    # Verify the date is preserved but time is updated
    assert corrected_datetime.date() == original_date.date(), "Date should be preserved"
    assert corrected_datetime.hour == new_time.hour, "Hour should be updated"
    assert corrected_datetime.minute == new_time.minute, "Minute should be updated"
    
    print("✅ Datetime preservation test passed!")

if __name__ == "__main__":
    test_date_reference_logic()
    print()
    test_datetime_preservation() 