#!/usr/bin/env python3
"""
Quick test for human-readable date formatting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import format_datetime_human_readable

def test_date_formatting():
    """Test the date formatting function"""
    
    test_cases = [
        "2025-05-28T00:00:00",  # Date only (midnight)
        "2025-05-28T15:00:00",  # 3 PM
        "2025-05-28T09:30:00",  # 9:30 AM
        "2025-12-25T12:00:00",  # Christmas noon
        "2025-01-01T23:59:00",  # New Year's Eve
    ]
    
    print("🧪 Testing human-readable date formatting:")
    print()
    
    for iso_date in test_cases:
        formatted = format_datetime_human_readable(iso_date)
        print(f"ISO: {iso_date}")
        print(f"Human: {formatted}")
        print()
    
    print("✅ Date formatting tests completed!")

if __name__ == "__main__":
    test_date_formatting() 