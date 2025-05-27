#!/usr/bin/env python3
"""
AI Agent for Weather-Aware Calendar Scheduling via Telegram
Uses Langchain + LangGraph + Gemini + Weather API + Google Calendar + Telegram Bot
"""

import os
import json
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, TypedDict
from dataclasses import dataclass

# Core dependencies
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Langchain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Google Calendar API
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DATA MODELS
# =============================================================================

class IntentExtraction(BaseModel):
    """Structured output for intent extraction from user message"""
    activity: str = Field(description="The activity the user wants to do")
    datetime_str: str = Field(description="Extracted date and time in ISO format")
    location: Optional[str] = Field(description="Location if mentioned", default=None)
    confidence: float = Field(description="Confidence score 0-1", default=0.0)
    is_weather_query: bool = Field(description="True if this is just a weather query, not scheduling", default=False)
    has_specific_time: bool = Field(description="True if user provided specific time, False if only date or vague", default=False)

class WeatherData(BaseModel):
    """Weather information structure"""
    temperature: float
    description: str
    is_rainy: bool
    humidity: int
    feels_like: Optional[float] = None

@dataclass
class AgentState(TypedDict):
    """State object for LangGraph agent"""
    user_message: str
    telegram_chat_id: int
    intent: Optional[IntentExtraction]
    weather: Optional[WeatherData]
    calendar_event_created: bool
    response_message: str
    needs_clarification: bool

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_datetime_human_readable(datetime_str: str) -> str:
    """Convert ISO datetime string to human-readable format"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        
        # Format: "28 May 2025, 3:00 PM" or "28 May 2025" if time is midnight
        if dt.hour == 0 and dt.minute == 0:
            return dt.strftime("%d %B %Y")
        else:
            return dt.strftime("%d %B %Y, %I:%M %p").replace(" 0", " ")  # Remove leading zero from hour
    except Exception as e:
        logger.error(f"Error formatting datetime: {e}")
        return datetime_str

# =============================================================================
# API CLIENTS
# =============================================================================

class GeminiClient:
    """Client for Gemini API using Langchain"""
    
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1
        )
        self.parser = PydanticOutputParser(pydantic_object=IntentExtraction)
    
    async def extract_intent(self, user_message: str) -> IntentExtraction:
        """Extract intent and datetime from user message"""
        system_prompt = """You are an AI assistant that extracts scheduling intent from natural language.
        
        ONLY extract scheduling information if the user is clearly trying to schedule an activity or event.
        
        Current date/time for reference: {current_time}
        
        IMPORTANT RULES:
        1. **NON-SCHEDULING MESSAGES**: If the user is just greeting (hello, hi, hey), asking general questions, 
           or having casual conversation WITHOUT mentioning scheduling/planning activities, set:
           - activity="casual conversation"
           - confidence=0.0 (very low confidence)
           
        2. **WEATHER QUERIES**: If asking about weather without scheduling (e.g., "what's the weather like", "how's the weather"), set:
           - is_weather_query=true
           - activity="weather query"
           
        3. **SCHEDULING REQUESTS**: Only if the user mentions wanting to DO something at a specific time/date:
           - "I want to go for a run tomorrow at 3pm"
           - "Schedule a meeting this Friday"
           - "Plan a picnic next Saturday"
           - Set confidence=0.8+ for clear scheduling intent
           
        4. **TIME SPECIFICITY**:
           - has_specific_time=true ONLY if user provides specific time (e.g., "3pm", "at 2:30", "9 in the morning")
           - has_specific_time=false if only date or vague time (e.g., "tomorrow", "this Saturday", "next week")
           
        5. **LOCATION**: Default to "Singapore" if no location specified
        
        Examples:
        - "hello" → activity="casual conversation", confidence=0.0
        - "how are you?" → activity="casual conversation", confidence=0.0  
        - "what's the weather?" → activity="weather query", is_weather_query=true
        - "I want to run tomorrow at 3pm" → activity="run", confidence=0.9, has_specific_time=true
        
        {format_instructions}
        """
        
        messages = [
            SystemMessage(content=system_prompt.format(
                current_time=datetime.now().isoformat(),
                format_instructions=self.parser.get_format_instructions()
            )),
            HumanMessage(content=user_message)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self.parser.parse(response.content)
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return IntentExtraction(
                activity="unknown",
                datetime_str=datetime.now().isoformat(),
                confidence=0.0
            )

class WeatherClient:
    """Client for OpenWeatherMap API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_weather_forecast(self, datetime_str: str, location: str = "Singapore") -> WeatherData:
        """Get weather forecast for specific datetime and location"""
        try:
            from datetime import datetime
            
            # Parse the target datetime
            target_dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            current_dt = datetime.now()
            
            # If the target time is more than 5 days away, use current weather as fallback
            # Otherwise, try to use the 5-day forecast endpoint
            if (target_dt - current_dt).days <= 5:
                # Use 5-day forecast endpoint for better accuracy
                url = f"{self.base_url}/forecast"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Find the closest forecast to the target time
                closest_forecast = None
                min_time_diff = float('inf')
                
                for forecast in data["list"]:
                    forecast_dt = datetime.fromtimestamp(forecast["dt"])
                    time_diff = abs((forecast_dt - target_dt).total_seconds())
                    
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_forecast = forecast
                
                if closest_forecast:
                    weather_desc = closest_forecast["weather"][0]["description"].lower()
                    is_rainy = any(word in weather_desc for word in ["rain", "drizzle", "shower"])
                    
                    return WeatherData(
                        temperature=closest_forecast["main"]["temp"],
                        description=closest_forecast["weather"][0]["description"],
                        is_rainy=is_rainy,
                        humidity=closest_forecast["main"]["humidity"],
                        feels_like=closest_forecast["main"].get("feels_like")
                    )
            
            # Fallback to current weather if forecast is not available or too far in future
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather_desc = data["weather"][0]["description"].lower()
            is_rainy = any(word in weather_desc for word in ["rain", "drizzle", "shower"])
            
            return WeatherData(
                temperature=data["main"]["temp"],
                description=data["weather"][0]["description"],
                is_rainy=is_rainy,
                humidity=data["main"]["humidity"],
                feels_like=data["main"].get("feels_like")
            )
            
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            # Return default non-rainy weather to avoid blocking
            return WeatherData(
                temperature=25.0,  # More realistic for Singapore
                description="clear sky",
                is_rainy=False,
                humidity=70,  # More realistic for Singapore
                feels_like=27.0
            )

class GoogleCalendarClient:
    """Client for Google Calendar API"""
    
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.json'
    
    def authenticate(self):
        """Authenticate with Google Calendar API using OAuth 2.0"""
        creds = None
        
        # Check if token.json exists (stored credentials)
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Google Calendar credentials")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file '{self.credentials_file}' not found. Please download it from Google Cloud Console.")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes)
                    creds = flow.run_local_server(port=0)
                    logger.info("Successfully authenticated with Google Calendar")
                except Exception as e:
                    logger.error(f"Error during OAuth flow: {e}")
                    return False
            
            # Save the credentials for the next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                logger.info("Saved Google Calendar credentials to token.json")
            except Exception as e:
                logger.error(f"Error saving credentials: {e}")
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error building Google Calendar service: {e}")
            return False
    
    async def create_event(self, intent: IntentExtraction) -> bool:
        """Create calendar event"""
        if not self.service:
            logger.error("Google Calendar service not initialized")
            return False
        
        try:
            # Parse the datetime
            from datetime import datetime, timedelta
            start_time = datetime.fromisoformat(intent.datetime_str.replace('Z', '+00:00'))
            
            # Default duration: 1 hour
            end_time = start_time + timedelta(hours=1)
            
            # Create event object
            event = {
                'summary': intent.activity,
                'location': intent.location or 'Singapore',
                'description': f'Scheduled via AI Calendar Bot\nActivity: {intent.activity}',
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
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},       # 30 minutes before
                    ],
                },
            }
            
            # Insert the event
            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Calendar event created: {event_result.get('htmlLink')}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return False

# =============================================================================
# LANGGRAPH AGENT NODES
# =============================================================================

async def extract_intent_node(state: AgentState) -> AgentState:
    """Node to extract intent from user message"""
    logger.info("Extracting intent from user message")
    
    gemini_client = GeminiClient(os.getenv("GEMINI_API_KEY"))
    intent = await gemini_client.extract_intent(state["user_message"])
    
    state["intent"] = intent
    logger.info(f"Extracted intent: {intent}")
    return state

async def check_weather_node(state: AgentState) -> AgentState:
    """Node to check weather for the planned activity"""
    logger.info("Checking weather forecast")
    
    if not state["intent"]:
        state["weather"] = None
        return state
    
    weather_client = WeatherClient(os.getenv("OPENWEATHER_API_KEY"))
    location = state["intent"].location or "Singapore"  # Default location
    
    weather = await weather_client.get_weather_forecast(
        state["intent"].datetime_str, 
        location
    )
    
    state["weather"] = weather
    logger.info(f"Weather check: {weather}")
    return state

async def weather_query_node(state: AgentState) -> AgentState:
    """Node to handle weather-only queries"""
    logger.info("Handling weather query")
    
    if not state["intent"]:
        state["response_message"] = "I couldn't understand your weather query. Please try again."
        return state
    
    weather_client = WeatherClient(os.getenv("OPENWEATHER_API_KEY"))
    location = state["intent"].location or "Singapore"  # Default location
    
    weather = await weather_client.get_weather_forecast(
        state["intent"].datetime_str, 
        location
    )
    
    state["weather"] = weather
    
    # Create comprehensive weather response
    response = f"🌤️ **Weather for {location.title()}**\n\n"
    response += f"🌡️ **Temperature**: {weather.temperature}°C"
    if weather.feels_like:
        response += f" (feels like {weather.feels_like}°C)"
    response += f"\n☁️ **Conditions**: {weather.description.title()}\n"
    response += f"💧 **Humidity**: {weather.humidity}%\n"
    
    # Add weather advice
    if weather.is_rainy:
        response += f"\n🌧️ **Advice**: It's rainy - bring an umbrella!"
    elif weather.temperature > 30:
        response += f"\n☀️ **Advice**: It's quite hot - stay hydrated!"
    elif weather.temperature < 20:
        response += f"\n🧥 **Advice**: It's cool - consider bringing a jacket!"
    else:
        response += f"\n✨ **Advice**: Great weather for outdoor activities!"
    
    state["response_message"] = response
    logger.info(f"Weather query response generated for {location}")
    return state

async def create_calendar_event_node(state: AgentState) -> AgentState:
    """Node to create calendar event"""
    logger.info("Creating calendar event")
    
    calendar_client = GoogleCalendarClient()
    calendar_client.authenticate()
    
    success = await calendar_client.create_event(state["intent"])
    state["calendar_event_created"] = success
    
    if success:
        formatted_time = format_datetime_human_readable(state["intent"].datetime_str)
        state["response_message"] = f"✅ Great! I've scheduled '{state['intent'].activity}' for {formatted_time}. The weather looks good!"
    else:
        state["response_message"] = "❌ Sorry, I couldn't create the calendar event. Please try again."
    
    return state

async def request_time_clarification_node(state: AgentState) -> AgentState:
    """Node to request time clarification when user doesn't provide specific time"""
    logger.info("Requesting time clarification")
    
    activity = state["intent"].activity
    date_part = format_datetime_human_readable(state["intent"].datetime_str)
    
    state["response_message"] = f"⏰ I see you want to {activity} on {date_part}, but what time would you prefer?\n\nFor example:\n• '3pm'\n• '2:30 in the afternoon'\n• '9 in the morning'\n• 'around lunchtime'"
    state["needs_clarification"] = True
    return state

async def casual_conversation_node(state: AgentState) -> AgentState:
    """Node to handle casual conversation and greetings"""
    logger.info("Handling casual conversation")
    
    user_message_lower = state["user_message"].lower()
    
    # Generate appropriate responses for different types of casual messages
    if any(greeting in user_message_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        state["response_message"] = "Hello! 👋 I'm your AI scheduling assistant. I can help you:\n\n📅 **Schedule activities** - Just tell me what you want to do and when!\n🌤️ **Check weather** - Ask about weather for any location\n\n**Examples:**\n• 'I want to go for a run tomorrow at 3pm'\n• 'Schedule a meeting this Friday at 2pm'\n• 'What's the weather like tomorrow?'\n\nHow can I help you today?"
    elif any(question in user_message_lower for question in ["how are you", "what's up", "how's it going"]):
        state["response_message"] = "I'm doing great, thank you! 😊 I'm here and ready to help you schedule activities and check the weather. What would you like to plan today?"
    elif any(thanks in user_message_lower for thanks in ["thank", "thanks", "appreciate"]):
        state["response_message"] = "You're very welcome! 😊 Feel free to ask me anytime if you need help scheduling activities or checking the weather!"
    else:
        # Generic casual conversation response
        state["response_message"] = "I'm your AI scheduling assistant! 🤖 I can help you schedule activities and check weather forecasts.\n\n**Try asking me:**\n• 'Schedule a workout tomorrow at 6pm'\n• 'What's the weather like this weekend?'\n• 'I want to have a picnic on Saturday'\n\nWhat would you like to plan?"
    
    return state

async def request_clarification_node(state: AgentState) -> AgentState:
    """Node to request clarification when weather is rainy or intent is unclear"""
    
    # Check if this is due to unclear intent or rainy weather
    if not state["intent"] or state["intent"].confidence <= 0.5 or state["intent"].activity == "unknown":
        logger.info("Requesting clarification due to unclear intent")
        state["response_message"] = "I'm not sure I understood what you'd like to do. Could you please be more specific?\n\n📅 **For scheduling:**\n• 'I want to go for a run at 4pm this Saturday'\n• 'Schedule a picnic tomorrow at 2pm'\n• 'Plan a bike ride next Tuesday morning'\n\n🌤️ **For weather queries:**\n• 'What's the weather like tomorrow?'\n• 'How's the weather this Saturday 3pm?'"
    else:
        logger.info("Requesting clarification due to rainy weather")
        weather_desc = state["weather"].description if state["weather"] else "rainy"
        formatted_time = format_datetime_human_readable(state["intent"].datetime_str)
        state["response_message"] = f"🌧️ The weather forecast shows {weather_desc} for your planned {state['intent'].activity} on {formatted_time}. Would you like to:\n\n1. Proceed anyway\n2. Reschedule to a different time\n3. Cancel the activity\n\nPlease let me know what you'd prefer!"
    
    state["needs_clarification"] = True
    return state

# =============================================================================
# LANGGRAPH ROUTING LOGIC
# =============================================================================

def should_check_weather(state: AgentState) -> str:
    """Router: decide if we should check weather, handle weather query, casual conversation, or request clarification"""
    if state["intent"]:
        # Handle casual conversation (greetings, general chat)
        if state["intent"].activity == "casual conversation" and state["intent"].confidence <= 0.1:
            return "casual_conversation"
        
        # Handle clear intents with good confidence
        if state["intent"].confidence > 0.5 and state["intent"].activity not in ["unknown", "casual conversation"]:
            if state["intent"].is_weather_query:
                return "weather_query"
            elif not state["intent"].has_specific_time:
                return "request_time_clarification"
            else:
                return "check_weather"
    
    # Default to clarification for unclear intents
    return "request_clarification"

def should_create_event(state: AgentState) -> str:
    """Router: decide if we should create calendar event or ask for clarification"""
    if state["weather"] and not state["weather"].is_rainy:
        return "create_event"
    else:
        return "request_clarification"

# =============================================================================
# LANGGRAPH WORKFLOW
# =============================================================================

def create_agent_workflow() -> StateGraph:
    """Create the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_intent", extract_intent_node)
    workflow.add_node("check_weather", check_weather_node)
    workflow.add_node("weather_query", weather_query_node)
    workflow.add_node("create_event", create_calendar_event_node)
    workflow.add_node("request_time_clarification", request_time_clarification_node)
    workflow.add_node("request_clarification", request_clarification_node)
    workflow.add_node("casual_conversation", casual_conversation_node)
    
    # Add edges
    workflow.set_entry_point("extract_intent")
    
    workflow.add_conditional_edges(
        "extract_intent",
        should_check_weather,
        {
            "check_weather": "check_weather",
            "weather_query": "weather_query",
            "request_time_clarification": "request_time_clarification",
            "request_clarification": "request_clarification",
            "casual_conversation": "casual_conversation"
        }
    )
    
    workflow.add_conditional_edges(
        "check_weather",
        should_create_event,
        {
            "create_event": "create_event",
            "request_clarification": "request_clarification"
        }
    )
    
    workflow.add_edge("create_event", END)
    workflow.add_edge("weather_query", END)
    workflow.add_edge("request_time_clarification", END)
    workflow.add_edge("request_clarification", END)
    workflow.add_edge("casual_conversation", END)
    
    return workflow.compile()

# =============================================================================
# TELEGRAM BOT
# =============================================================================

class TelegramBot:
    """Telegram bot handler"""
    
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.agent_workflow = create_agent_workflow()
        
        # Store conversation context for multi-turn conversations
        self.conversation_context = {}
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to your AI Scheduling Assistant!

I can help you with:
📅 **Schedule activities** - I'll check the weather and create calendar events
🌤️ **Weather queries** - Get comprehensive weather information

**Examples:**
• "I want to go for a run at 4pm this Saturday"
• "Schedule a picnic tomorrow at 2pm"
• "What's the weather like this Saturday 12pm?"
• "How's the weather in Tokyo tomorrow?"

I default to Singapore for weather unless you specify another location! 🇸🇬
        """
        await update.message.reply_text(welcome_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        # Check if message exists and has text
        if not update.message or not update.message.text:
            logger.info("Skipping non-text message or empty update")
            return
            
        user_message = update.message.text.strip()
        chat_id = update.effective_chat.id
        
        logger.info(f"Received message from {chat_id}: {user_message}")
        
        # Skip empty or very short messages
        if not user_message or len(user_message) < 2:
            logger.info("Skipping empty or very short message")
            return
        
        # Clean up old conversation contexts (older than 10 minutes)
        self.cleanup_old_contexts()
        
        # Check if this is a response to a clarification request
        # Only treat as clarification if it's a short response or contains clarification keywords
        if chat_id in self.conversation_context:
            # Check if this looks like a new scheduling request instead of a clarification
            scheduling_keywords = ["want", "schedule", "plan", "book", "at", "tomorrow", "today", "this", "next"]
            if any(keyword in user_message.lower() for keyword in scheduling_keywords) and len(user_message.split()) > 3:
                # This looks like a new request, clear old context and process as new
                logger.info("Detected new scheduling request, clearing old context")
                del self.conversation_context[chat_id]
            else:
                await self.handle_clarification_response(update, user_message, chat_id)
                return
        
        # Create initial state for new conversation
        initial_state = AgentState(
            user_message=user_message,
            telegram_chat_id=chat_id,
            intent=None,
            weather=None,
            calendar_event_created=False,
            response_message="",
            needs_clarification=False
        )
        
        try:
            # Run the agent workflow
            final_state = await self.agent_workflow.ainvoke(initial_state)
            
            # Store context for different types of clarification
            if final_state["needs_clarification"] and final_state["intent"]:
                if final_state["intent"].confidence > 0.5 and not final_state["intent"].has_specific_time:
                    # Time clarification needed
                    self.conversation_context[chat_id] = {
                        "original_intent": final_state["intent"],
                        "waiting_for": "time_clarification",
                        "timestamp": time.time()
                    }
                elif (final_state["intent"].confidence > 0.5 and 
                      final_state["weather"] and 
                      final_state["weather"].is_rainy):
                    # Weather clarification needed
                    self.conversation_context[chat_id] = {
                        "original_intent": final_state["intent"],
                        "weather": final_state["weather"],
                        "waiting_for": "weather_clarification",
                        "timestamp": time.time()
                    }
            
            # Send response back to user
            await update.message.reply_text(final_state["response_message"])
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("Sorry, I encountered an error. Please try again.")
    
    def cleanup_old_contexts(self):
        """Remove conversation contexts older than 10 minutes"""
        current_time = time.time()
        expired_chats = []
        
        for chat_id, context in self.conversation_context.items():
            if current_time - context.get("timestamp", 0) > 600:  # 10 minutes
                expired_chats.append(chat_id)
        
        for chat_id in expired_chats:
            logger.info(f"Cleaning up expired context for chat {chat_id}")
            del self.conversation_context[chat_id]
    
    async def handle_clarification_response(self, update: Update, user_message: str, chat_id: int):
        """Handle responses to clarification questions"""
        context = self.conversation_context[chat_id]
        user_message_lower = user_message.lower()
        
        logger.info(f"Handling clarification response: {user_message}")
        
        if context["waiting_for"] == "time_clarification":
            # Handle time clarification response
            await self.handle_time_clarification_response(update, user_message, chat_id, context)
        elif context["waiting_for"] == "weather_clarification":
            # Handle weather clarification response
            await self.handle_weather_clarification_response(update, user_message, chat_id, context)
    
    async def handle_time_clarification_response(self, update: Update, user_message: str, chat_id: int, context: dict):
        """Handle time clarification responses"""
        from datetime import datetime
        
        # Extract time from user's response using Gemini
        gemini_client = GeminiClient(os.getenv("GEMINI_API_KEY"))
        
        # Get the original date from the context
        original_intent = context["original_intent"]
        original_date = datetime.fromisoformat(original_intent.datetime_str.replace('Z', '+00:00'))
        
        # Create a combined message that preserves the original date context
        # Extract the relative date reference from the original datetime
        today = datetime.now().date()
        original_date_only = original_date.date()
        
        if original_date_only == today:
            date_reference = "today"
        elif (original_date_only - today).days == 1:
            date_reference = "tomorrow"
        elif (original_date_only - today).days == -1:
            date_reference = "yesterday"
        else:
            # Use the formatted date
            date_reference = original_date.strftime("%A")  # Day of week, or could use full date
        
        combined_message = f"I want to {original_intent.activity} {date_reference} at {user_message}"
        
        try:
            # Re-extract intent with the time information
            updated_intent = await gemini_client.extract_intent(combined_message)
            
            if updated_intent.has_specific_time and updated_intent.confidence > 0.7:
                # Verify the date is preserved correctly by manually setting it if needed
                updated_datetime = datetime.fromisoformat(updated_intent.datetime_str.replace('Z', '+00:00'))
                
                # If the date got reset to today when we meant a different day, fix it
                if updated_datetime.date() != original_date_only:
                    # Preserve the original date but use the new time
                    corrected_datetime = original_date.replace(
                        hour=updated_datetime.hour,
                        minute=updated_datetime.minute,
                        second=0,
                        microsecond=0
                    )
                    updated_intent.datetime_str = corrected_datetime.isoformat()
                
                # Time was successfully extracted, proceed with scheduling
                initial_state = AgentState(
                    user_message=combined_message,
                    telegram_chat_id=chat_id,
                    intent=updated_intent,
                    weather=None,
                    calendar_event_created=False,
                    response_message="",
                    needs_clarification=False
                )
                
                # Continue with weather check and scheduling
                final_state = await self.agent_workflow.ainvoke(initial_state)
                
                # Handle any further clarification needed (e.g., weather)
                if final_state["needs_clarification"] and final_state["weather"] and final_state["weather"].is_rainy:
                    self.conversation_context[chat_id] = {
                        "original_intent": final_state["intent"],
                        "weather": final_state["weather"],
                        "waiting_for": "weather_clarification",
                        "timestamp": time.time()
                    }
                else:
                    # Clear context if no further clarification needed
                    del self.conversation_context[chat_id]
                
                await update.message.reply_text(final_state["response_message"])
            else:
                # Time extraction failed, ask again
                response = "I couldn't understand the time. Could you please specify a time? For example:\n• '3pm'\n• '2:30 in the afternoon'\n• '9 in the morning'"
                await update.message.reply_text(response)
                # Keep context for another try
                
        except Exception as e:
            logger.error(f"Error processing time clarification: {e}")
            response = "Sorry, I had trouble understanding the time. Could you please try again?"
            await update.message.reply_text(response)
    
    async def handle_weather_clarification_response(self, update: Update, user_message: str, chat_id: int, context: dict):
        """Handle weather clarification responses"""
        user_message_lower = user_message.lower()
        
        # Parse the user's response
        if any(word in user_message_lower for word in ["1", "proceed", "yes", "continue", "anyway"]):
            # User wants to proceed anyway
            calendar_client = GoogleCalendarClient()
            calendar_client.authenticate()
            success = await calendar_client.create_event(context["original_intent"])
            
            if success:
                formatted_time = format_datetime_human_readable(context["original_intent"].datetime_str)
                response = f"✅ Great! I've scheduled '{context['original_intent'].activity}' for {formatted_time} despite the weather. Stay safe!"
            else:
                response = "❌ Sorry, I couldn't create the calendar event. Please try again."
                
        elif any(word in user_message_lower for word in ["2", "reschedule", "different", "later", "change"]):
            # User wants to reschedule
            response = "I'd be happy to help you reschedule! Please tell me when you'd prefer to do this activity instead."
            
        elif any(word in user_message_lower for word in ["3", "cancel", "no", "don't", "skip"]):
            # User wants to cancel
            response = f"No problem! I've cancelled your {context['original_intent'].activity} plan. Let me know if you'd like to schedule something else!"
            
        else:
            # Unclear response
            response = "I didn't quite understand. Please choose:\n\n1. Proceed anyway\n2. Reschedule to a different time\n3. Cancel the activity\n\nOr just type 'proceed', 'reschedule', or 'cancel'."
            await update.message.reply_text(response)
            return  # Keep the context for another try
        
        # Clear the conversation context and send response
        del self.conversation_context[chat_id]
        await update.message.reply_text(response)
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        # Clear any pending updates to avoid processing old messages
        self.app.run_polling(drop_pending_updates=True)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to run the AI agent"""
    
    # Check required environment variables
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "GEMINI_API_KEY",
        "OPENWEATHER_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set them in your .env file or environment")
        return
    
    # Initialize and run the bot
    bot = TelegramBot(os.getenv("TELEGRAM_BOT_TOKEN"))
    bot.run()

if __name__ == "__main__":
    main() 