import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """Authenticate and return the Google Calendar service."""
    creds = None
    # Check if token.json exists (stores user's access and refresh tokens)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_task_to_calendar(task_title, task_description, task_due_date):
    """Add a task to Google Calendar."""
    service = authenticate_google_calendar()

    # Create an event
    event = {
        'summary': task_title,
        'description': task_description,
        'start': {
            'dateTime': task_due_date.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (task_due_date + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
    }

    # Insert the event into the user's calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Task added to calendar: {event.get('htmlLink')}")