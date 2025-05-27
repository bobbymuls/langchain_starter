#!/usr/bin/env python3
"""
Test script for AI Weather-Aware Scheduling Agent
Tests individual components without requiring full Telegram bot setup
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import our main components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import (
    GeminiClient, WeatherClient, GoogleCalendarClient,
    IntentExtraction, WeatherData, AgentState,
    create_agent_workflow
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gemini_client():
    """Test Gemini AI intent extraction"""
    print("\n🧠 Testing Gemini AI Intent Extraction...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    try:
        client = GeminiClient(api_key)
        test_message = "I want to go for a run at 4pm this Saturday"
        
        intent = await client.extract_intent(test_message)
        print(f"✅ Intent extracted: {intent}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

async def test_weather_client():
    """Test OpenWeatherMap API"""
    print("\n🌤️ Testing Weather API...")
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key or api_key.startswith("your_"):
        print("❌ OPENWEATHER_API_KEY not configured")
        return False
    
    try:
        client = WeatherClient(api_key)
        weather = await client.get_weather_forecast(
            datetime.now().isoformat(), 
            "London"
        )
        print(f"✅ Weather data: {weather}")
        return True
        
    except Exception as e:
        print(f"❌ Weather test failed: {e}")
        return False

async def test_calendar_client():
    """Test Google Calendar client (mock)"""
    print("\n📅 Testing Calendar Client...")
    
    try:
        client = GoogleCalendarClient()
        client.authenticate()
        
        test_intent = IntentExtraction(
            activity="test run",
            datetime_str=datetime.now().isoformat(),
            confidence=0.9
        )
        
        success = await client.create_event(test_intent)
        print(f"✅ Calendar test: {'Success' if success else 'Failed'}")
        return success
        
    except Exception as e:
        print(f"❌ Calendar test failed: {e}")
        return False

async def test_langgraph_workflow():
    """Test the complete LangGraph workflow"""
    print("\n🔄 Testing LangGraph Workflow...")
    
    try:
        workflow = create_agent_workflow()
        
        # Test state
        test_state = AgentState(
            user_message="I want to go for a run tomorrow at 3pm",
            telegram_chat_id=12345,
            intent=None,
            weather=None,
            calendar_event_created=False,
            response_message="",
            needs_clarification=False
        )
        
        # Run workflow (this will test the full flow)
        final_state = await workflow.ainvoke(test_state)
        print(f"✅ Workflow completed: {final_state['response_message']}")
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_environment_setup():
    """Test environment variable configuration"""
    print("\n🔧 Testing Environment Setup...")
    
    required_vars = [
        "GEMINI_API_KEY",
        "OPENWEATHER_API_KEY", 
        "TELEGRAM_BOT_TOKEN"
    ]
    
    missing_vars = []
    configured_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
        else:
            configured_vars.append(var)
    
    print(f"✅ Configured: {configured_vars}")
    if missing_vars:
        print(f"❌ Missing: {missing_vars}")
        return False
    
    return True

async def run_all_tests():
    """Run all tests"""
    print("🧪 AI Agent Component Tests")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Test results
    results = {}
    
    # Test environment setup
    results["environment"] = test_environment_setup()
    
    # Test individual components
    if results["environment"]:
        results["gemini"] = await test_gemini_client()
        results["weather"] = await test_weather_client()
        results["calendar"] = await test_calendar_client()
        
        # Test full workflow only if individual components work
        if results["gemini"]:
            results["workflow"] = await test_langgraph_workflow()
        else:
            results["workflow"] = False
    else:
        print("\n⚠️ Skipping API tests due to missing environment variables")
        results.update({
            "gemini": False,
            "weather": False, 
            "calendar": False,
            "workflow": False
        })
    
    # Print summary
    print("\n📊 Test Summary:")
    print("-" * 20)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.capitalize()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your agent is ready to run.")
    else:
        print("⚠️ Some tests failed. Check configuration and API keys.")
    
    return passed_tests == total_tests

def main():
    """Main test function"""
    try:
        success = asyncio.run(run_all_tests())
        return success
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 