"""
Google Calendar Helper Module
Handles all Google Calendar API operations for appointment scheduling
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from zoneinfo import ZoneInfo
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import configuration from settings
from config.settings import (
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_CALENDAR_ID,
    DEFAULT_TIMEZONE,
    DEFAULT_REMINDERS
)

# Timezone constants
ISRAEL_TZ = ZoneInfo(DEFAULT_TIMEZONE)  # Asia/Jerusalem
UTC_TZ = ZoneInfo('UTC')

# =============================================================================
# CONFIGURATION
# =============================================================================

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# =============================================================================
# GOOGLE CALENDAR API CLIENT
# =============================================================================

class GoogleCalendarHelper:
    """Helper class for Google Calendar API operations"""

    def __init__(self):
        """Initialize Google Calendar API service"""
        self.credentials_path = GOOGLE_CREDENTIALS_PATH
        self.calendar_id = GOOGLE_CALENDAR_ID
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Calendar API service with service account credentials"""
        try:
            # Try to load credentials from environment variable first (for Railway)
            google_creds_json = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')

            if google_creds_json:
                # Load credentials from environment variable
                print("📋 Loading Google Calendar credentials from environment variable")
                credentials_info = json.loads(google_creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=SCOPES
                )
            elif os.path.exists(self.credentials_path):
                # Load credentials from file (for local development)
                print(f"📋 Loading Google Calendar credentials from file: {self.credentials_path}")
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=SCOPES
                )
            else:
                print(f"❌ Google Calendar credentials not found")
                print("   Set GOOGLE_CALENDAR_CREDENTIALS env var or provide credentials file")
                print("⚠️  Calendar integration will be disabled")
                self.service = None
                return

            # Build the Calendar API service
            self.service = build('calendar', 'v3', credentials=credentials)
            print(f"✅ Google Calendar service initialized successfully")
            print(f"📅 Using calendar: {self.calendar_id}")

        except Exception as e:
            print(f"❌ Error initializing Google Calendar service: {str(e)}")
            print("⚠️  Calendar integration will be disabled")
            self.service = None

    def create_event(self,
                     title: str,
                     date: str,
                     time: str,
                     duration: int = 60,
                     notes: str = "",
                     language: str = "english") -> Dict:
        """
        Create a calendar event

        Args:
            title: Event title
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format (24-hour)
            duration: Duration in minutes (default: 60)
            notes: Additional notes for the event
            language: Language for response message (hebrew/english)

        Returns:
            dict with 'success' (bool), 'message' (str), 'event_link' (str or None), 'event_id' (str or None)
        """

        # Check if service is initialized
        if self.service is None:
            if language == "hebrew":
                return {
                    'success': False,
                    'message': "❌ שירות גוגל קלנדר לא מוגדר. אנא הגדר את קובץ האישורים.",
                    'event_link': None,
                    'event_id': None
                }
            else:
                return {
                    'success': False,
                    'message': "❌ Google Calendar service not configured. Please set up credentials file.",
                    'event_link': None,
                    'event_id': None
                }

        try:
            # Parse date and time
            start_datetime = self._parse_datetime(date, time)
            end_datetime = start_datetime + timedelta(minutes=duration)

            # Check for conflicts
            conflict = self._check_time_conflict(start_datetime, end_datetime)
            if conflict:
                if language == "hebrew":
                    message = f"""⚠️ המשבצת תפוסה!
📅 תאריך: {date}
🕐 שעה: {time}
❌ הזמן הזה כבר תפוס

אנא בחר זמן אחר."""
                else:
                    message = f"""⚠️ Time slot is occupied!
📅 Date: {date}
🕐 Time: {time}
❌ This time is already booked

Please choose another time."""

                return {
                    'success': False,
                    'message': message,
                    'event_link': None,
                    'event_id': None
                }

            # Prepare event body
            event = {
                'summary': title,
                'description': notes,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': DEFAULT_TIMEZONE,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': DEFAULT_TIMEZONE,
                },
                'reminders': DEFAULT_REMINDERS,
            }

            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            # Prepare success message
            if language == "hebrew":
                message = f"""✅ הפגישה נקבעה בהצלחה!
📅 תאריך: {date}
🕐 שעה: {time}
⏱️ משך: {duration} דקות
📝 נושא: {title}"""
            else:
                message = f"""✅ Appointment scheduled successfully!
📅 Date: {date}
🕐 Time: {time}
⏱️ Duration: {duration} minutes
📝 Title: {title}"""

            return {
                'success': True,
                'message': message,
                'event_link': created_event.get('htmlLink'),
                'event_id': created_event.get('id')
            }

        except HttpError as error:
            print(f"❌ Google Calendar API error: {error}")

            if language == "hebrew":
                error_message = f"❌ שגיאה בקביעת הפגישה: {str(error)}"
            else:
                error_message = f"❌ Error scheduling appointment: {str(error)}"

            return {
                'success': False,
                'message': error_message,
                'event_link': None,
                'event_id': None
            }

        except Exception as e:
            print(f"❌ Unexpected error creating calendar event: {str(e)}")

            if language == "hebrew":
                error_message = f"❌ שגיאה לא צפויה: {str(e)}"
            else:
                error_message = f"❌ Unexpected error: {str(e)}"

            return {
                'success': False,
                'message': error_message,
                'event_link': None,
                'event_id': None
            }

    def _check_time_conflict(self, start_datetime: datetime, end_datetime: datetime) -> Optional[Dict]:
        """
        Check if there's a conflicting event in the calendar

        Args:
            start_datetime: Start time of proposed event (timezone-aware, Israel time)
            end_datetime: End time of proposed event (timezone-aware, Israel time)

        Returns:
            Dict with conflict details if found, None otherwise
        """
        try:
            # Convert Israel time to UTC for API query
            start_utc = start_datetime.astimezone(UTC_TZ)
            end_utc = end_datetime.astimezone(UTC_TZ)

            # Query events in the time range (API expects RFC3339 format)
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                timeMax=end_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Check if any event overlaps
            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))

                # Parse event times to timezone-aware datetimes
                event_start_dt = self._parse_event_datetime(event_start)
                event_end_dt = self._parse_event_datetime(event_end)

                # Check for overlap (both are now timezone-aware)
                if (start_datetime < event_end_dt and end_datetime > event_start_dt):
                    # Convert to Israel time for display
                    event_start_israel = event_start_dt.astimezone(ISRAEL_TZ)
                    event_end_israel = event_end_dt.astimezone(ISRAEL_TZ)
                    return {
                        'summary': event.get('summary', 'Untitled'),
                        'start_time': event_start_israel.strftime('%H:%M'),
                        'end_time': event_end_israel.strftime('%H:%M')
                    }

            return None

        except Exception as e:
            print(f"⚠️ Error checking for conflicts: {str(e)}")
            return None  # If check fails, allow booking (fail open)

    def _parse_event_datetime(self, dt_string: str) -> datetime:
        """
        Parse event datetime string from Google Calendar API to timezone-aware datetime

        Args:
            dt_string: DateTime string from API (can be ISO format with timezone or date only)

        Returns:
            Timezone-aware datetime object
        """
        try:
            # Handle 'Z' suffix (UTC)
            if dt_string.endswith('Z'):
                dt_string = dt_string[:-1] + '+00:00'

            # Parse ISO format with timezone
            parsed = datetime.fromisoformat(dt_string)

            # If no timezone info, assume Israel timezone
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=ISRAEL_TZ)

            return parsed

        except ValueError:
            # Handle date-only format (all-day events)
            parsed = datetime.strptime(dt_string, '%Y-%m-%d')
            return parsed.replace(tzinfo=ISRAEL_TZ)

    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """
        Parse date and time strings into timezone-aware datetime object

        Args:
            date_str: Date in YYYY-MM-DD format
            time_str: Time in HH:MM format (24-hour)

        Returns:
            Timezone-aware datetime object in Israel timezone (Asia/Jerusalem)
        """
        try:
            # Combine date and time
            datetime_str = f"{date_str} {time_str}"
            parsed_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

            # Add Israel timezone to make it timezone-aware
            parsed_datetime = parsed_datetime.replace(tzinfo=ISRAEL_TZ)

            return parsed_datetime

        except ValueError as e:
            raise ValueError(f"Invalid date/time format: {str(e)}")

# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_calendar_helper = None

def get_calendar_helper() -> GoogleCalendarHelper:
    """Get or create GoogleCalendarHelper singleton instance"""
    global _calendar_helper
    if _calendar_helper is None:
        _calendar_helper = GoogleCalendarHelper()
    return _calendar_helper
