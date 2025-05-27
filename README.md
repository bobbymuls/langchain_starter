# AI Agent for Weather-Aware Calendar Scheduling via Telegram

A sophisticated AI-powered Telegram bot that helps users schedule activities by checking weather conditions and automatically creating Google Calendar events. Built with LangChain, LangGraph, Google Gemini AI, and integrated with Google Calendar API.

## 🌟 Features

### 🤖 **Intelligent Conversation Handling**
- **Smart Intent Recognition**: Distinguishes between casual conversation, weather queries, and scheduling requests
- **Natural Language Processing**: Understands various ways of expressing scheduling intent
- **Context-Aware Responses**: Maintains conversation context for multi-turn interactions

### 📅 **Advanced Scheduling**
- **Automatic Calendar Integration**: Creates real Google Calendar events with proper details
- **Time Clarification**: Asks for specific times when users provide only dates
- **Weather-Aware Decisions**: Checks weather conditions before scheduling outdoor activities
- **Flexible Rescheduling**: Offers options when weather conditions are unfavorable

### 🌤️ **Weather Intelligence**
- **5-Day Forecast**: Uses OpenWeatherMap API for accurate weather predictions
- **Location Support**: Supports weather queries for any global location (defaults to Singapore)
- **Weather-Based Recommendations**: Provides advice based on weather conditions
- **Rainy Day Handling**: Offers alternatives when weather is unsuitable for planned activities

### 🔐 **Secure Authentication**
- **OAuth 2.0 Integration**: Secure Google Calendar API authentication
- **Token Persistence**: Automatic credential management and refresh
- **Privacy-First**: All credentials stored locally and excluded from version control

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Console account
- Telegram Bot Token
- OpenWeatherMap API key
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd langchain_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Calendar API**
   - Follow the detailed guide in `docs/GOOGLE_CALENDAR_SETUP.md`
   - Download `credentials.json` from Google Cloud Console
   - Place it in the project root directory

4. **Configure environment variables**
   Create a `.env` file with:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## 💬 Usage Examples

### Casual Conversation
```
User: hello
Bot: Hello! 👋 I'm your AI scheduling assistant. I can help you:
     📅 Schedule activities - Just tell me what you want to do and when!
     🌤️ Check weather - Ask about weather for any location
```

### Weather Queries
```
User: What's the weather like tomorrow?
Bot: 🌤️ Weather for Singapore
     🌡️ Temperature: 29°C (feels like 33°C)
     ☁️ Conditions: Overcast Clouds
     💧 Humidity: 71%
```

### Activity Scheduling
```
User: I want to go for a run tomorrow
Bot: ⏰ I see you want to go for a run on 29 May 2025, but what time would you prefer?

User: 6am
Bot: ✅ Great! I've scheduled 'go for a run' for 29 May 2025, 6:00 AM. The weather looks good!
```

### Weather-Aware Scheduling
```
User: I want to have a picnic this Saturday at 2pm
Bot: 🌧️ The weather forecast shows light rain for your planned picnic on 30 May 2025, 2:00 PM. 
     Would you like to:
     1. Proceed anyway
     2. Reschedule to a different time
     3. Cancel the activity
```

## 🏗️ Architecture

### Core Components

- **LangGraph Workflow**: State-based conversation flow management
- **Google Gemini AI**: Advanced natural language understanding
- **Google Calendar API**: Real calendar event creation and management
- **OpenWeatherMap API**: Accurate weather forecasting
- **Telegram Bot API**: User interface and messaging

### Workflow States

1. **Intent Extraction**: Analyze user message for scheduling intent
2. **Weather Check**: Fetch weather conditions for planned activities
3. **Calendar Creation**: Create Google Calendar events
4. **Clarification Handling**: Manage multi-turn conversations for missing information

## 🧪 Testing

The project includes comprehensive test scripts:

- **`test_scripts/test_google_calendar_fixed.py`**: Tests Google Calendar API integration
- **`test_scripts/test_main_calendar.py`**: Tests calendar functionality from main script

Run tests:
```bash
python test_scripts/test_google_calendar_fixed.py
python test_scripts/test_main_calendar.py
```

## 📁 Project Structure

```
langchain_project/
├── main.py                           # Main bot application
├── credentials.json                  # Google OAuth credentials (not in git)
├── token.json                       # Saved authentication token (not in git)
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (not in git)
├── README.md                       # This file
├── test_scripts/                   # Test utilities
│   ├── test_google_calendar_fixed.py
│   └── test_main_calendar.py
└── docs/                          # Documentation
    └── GOOGLE_CALENDAR_SETUP.md    # Complete setup and troubleshooting guide
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather | Yes |
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Yes |

### Google Calendar Setup

1. Create Google Cloud Project
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download credentials as `credentials.json`
5. Run the bot - it will handle OAuth flow automatically

Detailed setup instructions: `docs/GOOGLE_CALENDAR_SETUP.md`

## 🛡️ Security Features

- **Credential Protection**: All sensitive files in `.gitignore`
- **OAuth 2.0**: Secure Google API authentication
- **Token Management**: Automatic refresh and secure storage
- **Input Validation**: Robust error handling and input sanitization

## 🌍 Supported Features

- **Global Weather**: Weather queries for any location worldwide
- **Timezone Handling**: Proper timezone management (defaults to Asia/Singapore)
- **Multi-language**: Supports various natural language expressions
- **Error Recovery**: Graceful handling of API failures and network issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Setup Issues**: Check `docs/GOOGLE_CALENDAR_SETUP.md`
- **General Questions**: Open an issue on GitHub

## 🎯 Recent Updates

### v2.0.0 - Google Calendar Integration
- ✅ **Full Google Calendar API integration**
- ✅ **Improved intent classification** (handles greetings properly)
- ✅ **Enhanced conversation flow** with casual conversation support
- ✅ **Robust OAuth 2.0 authentication** with automatic token management
- ✅ **Comprehensive testing suite** for calendar functionality
- ✅ **Weather-aware scheduling** with intelligent recommendations

---

**Built with ❤️ using LangChain, LangGraph, and Google AI** 