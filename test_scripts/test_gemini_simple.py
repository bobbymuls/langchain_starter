#!/usr/bin/env python3
"""
Simple test script to verify Gemini API key is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API with a simple request"""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    try:
        # Import and test Gemini
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Create client
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Get user input
        user_message = input("\n💬 Enter your message for Gemini: ")
        
        # Send user's message to Gemini
        response = llm.invoke(user_message)
        
        print(f"\n✅ Gemini API Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Testing Gemini API Key...")
    print("=" * 30)
    
    success = test_gemini_api()
    
    if success:
        print("\n🎉 Gemini API is working correctly!")
    else:
        print("\n⚠️ Gemini API test failed. Check your API key.") 