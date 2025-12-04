"""
Configuration settings for WhatsApp Appointment Scheduler
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"
CONFIG_DIR = PROJECT_ROOT / "config"

# Google Calendar settings
DEFAULT_TIMEZONE = "Asia/Jerusalem"
DEFAULT_APPOINTMENT_DURATION = 60  # minutes

# Reminder settings
DEFAULT_REMINDERS = {
    'useDefault': False,
    'overrides': [
        {'method': 'popup', 'minutes': 30},
        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
    ],
}

# Google Calendar credentials
GOOGLE_CREDENTIALS_PATH = os.getenv(
    'GOOGLE_CALENDAR_CREDENTIALS_PATH',
    str(CREDENTIALS_DIR / 'google_calendar_credentials.json')
)
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')

if not GOOGLE_CALENDAR_ID:
    raise ValueError("GOOGLE_CALENDAR_ID must be set in .env file")

# Twilio settings (validated in app.py)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Flask settings
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
