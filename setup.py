#!/usr/bin/env python3
"""
Setup script for AI Weather-Aware Scheduling Agent
Helps with initial project configuration and dependency installation
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required. Current version:", sys.version)
        return False
    print("✅ Python version check passed:", sys.version.split()[0])
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("\n🔧 Creating .env file...")
    env_template = """# Telegram Bot Token (get from @BotFather on Telegram)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Gemini API Key (get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenWeatherMap API Key (get from openweathermap.org)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Google Calendar API credentials (optional - currently using mock)
# GOOGLE_CALENDAR_CREDENTIALS_PATH=path/to/credentials.json
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ .env file created successfully")
        print("⚠️  Please edit .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_api_keys():
    """Check if required API keys are configured"""
    print("\n🔑 Checking API key configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_keys = [
            ("TELEGRAM_BOT_TOKEN", "Telegram Bot"),
            ("GEMINI_API_KEY", "Gemini AI"),
            ("OPENWEATHER_API_KEY", "OpenWeatherMap")
        ]
        
        missing_keys = []
        for key, name in required_keys:
            value = os.getenv(key)
            if not value or value.startswith("your_"):
                missing_keys.append(name)
                print(f"❌ {name} API key not configured")
            else:
                print(f"✅ {name} API key configured")
        
        if missing_keys:
            print(f"\n⚠️  Please configure the following API keys in .env file:")
            for key in missing_keys:
                print(f"   - {key}")
            return False
        
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print("\n🚀 Setup Complete! Next steps:")
    print("1. Edit .env file with your actual API keys")
    print("2. Get Telegram bot token from @BotFather")
    print("3. Get OpenWeatherMap API key from openweathermap.org")
    print("4. Test the setup: python test_scripts/test_agent.py")
    print("5. Run the agent: python main.py")
    print("\n📖 See README.md for detailed setup instructions")

def main():
    """Main setup function"""
    print("🤖 AI Weather-Aware Scheduling Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check API keys
    keys_configured = check_api_keys()
    
    # Print next steps
    print_next_steps()
    
    if not keys_configured:
        print("\n⚠️  Setup completed but API keys need configuration")
        return False
    
    print("\n✅ Setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 