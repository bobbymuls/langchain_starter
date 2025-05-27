#!/usr/bin/env python3
"""
Quick test for weather forecast functionality
"""

import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

# Import our weather client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import WeatherClient

async def test_weather_forecast():
    """Test the weather forecast functionality"""
    
    weather_client = WeatherClient(os.getenv("OPENWEATHER_API_KEY"))
    
    # Test 1: Current weather for Singapore
    print("🧪 Test 1: Current weather for Singapore")
    current_time = datetime.now().isoformat()
    weather = await weather_client.get_weather_forecast(current_time, "Singapore")
    print(f"Temperature: {weather.temperature}°C")
    print(f"Conditions: {weather.description}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Is rainy: {weather.is_rainy}")
    if weather.feels_like:
        print(f"Feels like: {weather.feels_like}°C")
    print()
    
    # Test 2: Tomorrow's weather
    print("🧪 Test 2: Tomorrow's weather for Singapore")
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    weather = await weather_client.get_weather_forecast(tomorrow, "Singapore")
    print(f"Temperature: {weather.temperature}°C")
    print(f"Conditions: {weather.description}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Is rainy: {weather.is_rainy}")
    if weather.feels_like:
        print(f"Feels like: {weather.feels_like}°C")
    print()
    
    # Test 3: Specific time tomorrow
    print("🧪 Test 3: Tomorrow 3PM for Singapore")
    tomorrow_3pm = (datetime.now() + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0).isoformat()
    weather = await weather_client.get_weather_forecast(tomorrow_3pm, "Singapore")
    print(f"Temperature: {weather.temperature}°C")
    print(f"Conditions: {weather.description}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Is rainy: {weather.is_rainy}")
    if weather.feels_like:
        print(f"Feels like: {weather.feels_like}°C")
    print()
    
    print("✅ Weather forecast tests completed!")

if __name__ == "__main__":
    asyncio.run(test_weather_forecast()) 