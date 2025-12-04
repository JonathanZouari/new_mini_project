from crewai import Agent, Crew, Task, Process
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
from pathlib import Path
import os
import json
import re
import yaml

# =============================================================================
# CREWAI CONFIGURATION
# =============================================================================

# Load environment variables FIRST (with override to ensure fresh load)
load_dotenv(override=True)

# Import google_calendar_helper AFTER loading .env
from google_calendar_helper import get_calendar_helper

# Set OpenAI API key for CrewAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Load configuration files
CONFIG_DIR = Path(__file__).parent / "config"

def load_yaml_config(filename: str) -> dict:
    """Load YAML configuration file with UTF-8 encoding for Hebrew support"""
    try:
        with open(CONFIG_DIR / filename, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise RuntimeError(f"Failed to load {filename}: {e}")

# Load all configs
AGENTS_CONFIG = load_yaml_config("agents.yaml")
TASKS_CONFIG = load_yaml_config("tasks.yaml")
MESSAGES_CONFIG = load_yaml_config("messages.yaml")

# =============================================================================
# STATE MODEL
# =============================================================================

class AppointmentState(BaseModel):
    """State that flows through the system"""
    user_message: str = ""
    user_phone: str = ""
    category: str = ""  # GENERAL, APPOINTMENT, UNRELATED
    language: str = "english"
    calendar_data: Optional[dict] = None
    response: str = ""
    event_created: bool = False

# =============================================================================
# AGENTS (loaded from agents.yaml)
# =============================================================================

router_agent = Agent(**AGENTS_CONFIG['router_agent'])
general_agent = Agent(**AGENTS_CONFIG['general_agent'])
extractor_agent = Agent(**AGENTS_CONFIG['extractor_agent'])

# =============================================================================
# APPOINTMENT FLOW
# =============================================================================

class AppointmentFlow(Flow[AppointmentState]):
    """
    Main Flow for WhatsApp Appointment System

    WhatsApp → Route → [APPOINTMENT] → Extract → Calendar API
                     → [GENERAL] → Answer → WhatsApp
                     → [UNRELATED] → Redirect → WhatsApp
    """

    # -------------------------------------------------------------------------
    # STEP 1: Route the message
    # -------------------------------------------------------------------------
    @start()
    def route_message(self):
        """First step: classify the incoming message"""
        print(f"\n🔍 Routing: {self.state.user_message}")

        # Load task description from YAML
        description = TASKS_CONFIG['route_message']['description'].format(
            user_message=self.state.user_message
        )

        task = Task(
            description=description,
            expected_output=TASKS_CONFIG['route_message']['expected_output'],
            agent=router_agent
        )

        crew = Crew(agents=[router_agent], tasks=[task], verbose=True)
        result = str(crew.kickoff())

        # Parse result
        data = self._parse_json(result)
        self.state.category = data.get("category", "UNRELATED").upper()
        self.state.language = data.get("language", "english")

        print(f"📊 Category: {self.state.category}, Language: {self.state.language}")
        return self.state.category

    # -------------------------------------------------------------------------
    # ROUTER: Decide which path to take
    # -------------------------------------------------------------------------
    @router(route_message)
    def select_path(self):
        """Route to the appropriate handler based on category"""
        if "APPOINTMENT" in self.state.category:
            return "appointment"
        elif "GENERAL" in self.state.category:
            return "general"
        else:
            return "unrelated"

    # -------------------------------------------------------------------------
    # PATH A: Appointment Creation (פגישה)
    # -------------------------------------------------------------------------
    @listen("appointment")
    def extract_datetime(self):
        """Extract date/time from appointment request"""
        print(f"\n📅 Extracting datetime...")

        today = datetime.now().strftime("%Y-%m-%d")

        # Load task description from YAML
        description = TASKS_CONFIG['extract_datetime']['description'].format(
            user_message=self.state.user_message,
            today=today
        )

        task = Task(
            description=description,
            expected_output=TASKS_CONFIG['extract_datetime']['expected_output'],
            agent=extractor_agent
        )

        crew = Crew(agents=[extractor_agent], tasks=[task], verbose=True)
        result = str(crew.kickoff())

        self.state.calendar_data = self._parse_json(result)
        print(f"📊 Extracted: {self.state.calendar_data}")

    @listen(extract_datetime)
    def create_calendar_event(self):
        """Create event in Google Calendar"""
        print(f"\n🗓️ Creating calendar event...")

        if not self.state.calendar_data:
            # Load error message from YAML
            self.state.response = MESSAGES_CONFIG['responses']['extraction_failed'][self.state.language]
            return

        event_data = self.state.calendar_data

        # Create event using Google Calendar Helper
        calendar_helper = get_calendar_helper()
        result = calendar_helper.create_event(
            title=event_data.get('title', 'Appointment'),
            date=event_data.get('date'),
            time=event_data.get('time'),
            duration=event_data.get('duration', 60),
            notes=event_data.get('notes', ''),
            language=self.state.language
        )

        # Update state with result
        self.state.event_created = result['success']
        self.state.response = result['message']

        if result['success']:
            print(f"✅ Event created successfully!")
            if result.get('event_link'):
                print(f"🔗 Event link: {result['event_link']}")
        else:
            print(f"❌ Event creation failed: {result['message']}")

    # -------------------------------------------------------------------------
    # PATH B: General Questions (כללי)
    # -------------------------------------------------------------------------
    @listen("general")
    def answer_general_question(self):
        """Answer general scheduling questions"""
        print(f"\n💬 Answering general question...")

        # Load task description from YAML
        description = TASKS_CONFIG['answer_general']['description'].format(
            user_message=self.state.user_message,
            language=self.state.language
        )

        task = Task(
            description=description,
            expected_output=TASKS_CONFIG['answer_general']['expected_output'],
            agent=general_agent
        )

        crew = Crew(agents=[general_agent], tasks=[task], verbose=True)
        self.state.response = str(crew.kickoff())

        print(f"💬 Response ready")

    # -------------------------------------------------------------------------
    # PATH C: Unrelated Message
    # -------------------------------------------------------------------------
    @listen("unrelated")
    def handle_unrelated(self):
        """Handle messages not related to scheduling"""
        print(f"\n🚫 Unrelated message...")

        # Load unrelated message from YAML
        self.state.response = MESSAGES_CONFIG['responses']['unrelated'][self.state.language]

    # -------------------------------------------------------------------------
    # FINAL STEP: Send to WhatsApp
    # -------------------------------------------------------------------------
    @listen(create_calendar_event)
    @listen(answer_general_question)
    @listen(handle_unrelated)
    def send_to_whatsapp(self):
        """Send the response back to WhatsApp"""
        print(f"\n📤 Sending to WhatsApp: {self.state.user_phone}")
        print(f"📨 Response: {self.state.response}")

        # ====== TWILIO WHATSAPP API CALL WOULD GO HERE ======
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(
        #     body=self.state.response,
        #     from_='whatsapp:+14155238886',
        #     to=self.state.user_phone
        # )
        # ====================================================

        return self.state.response

    # -------------------------------------------------------------------------
    # HELPER
    # -------------------------------------------------------------------------
    def _parse_json(self, text: str) -> dict:
        """Extract JSON from text"""
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {}

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def process_whatsapp_message(message: str, phone: str = "") -> str:
    """Process a WhatsApp message through the flow"""
    flow = AppointmentFlow()
    flow.state.user_message = message
    flow.state.user_phone = phone

    result = flow.kickoff()
    return flow.state.response

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    test_messages = [
        ("Schedule a meeting for tomorrow at 3pm", "+972501234567"),
        ("How do I book an appointment?", "+972501234567"),
        ("קבע לי פגישה מחר בשעה 10", "+972501234567"),
        ("What's the weather?", "+972501234567"),
    ]

    print("=" * 60)
    print("🚀 CREWAI FLOW - APPOINTMENT SYSTEM")
    print("=" * 60)

    for msg, phone in test_messages:
        print(f"\n{'='*60}")
        print(f"📨 Message: {msg}")
        print(f"📱 Phone: {phone}")
        print("="*60)

        response = process_whatsapp_message(msg, phone)

        print(f"\n✅ FINAL RESPONSE:")
        print(response)
        print("="*60)