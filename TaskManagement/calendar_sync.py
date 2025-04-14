import datetime  # Import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from TaskManagement.database import db_sessions  

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

try:
    service = authenticate_google_calendar()  # Use the function to get the service object

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    event_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = event_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

except HttpError as error:
    # Handle errors from the API
    print('An error occurred:', error)

def add_task_to_calendar(task, task_title, task_description, task_due_date):
    """Add a task to Google Calendar."""
    service = authenticate_google_calendar()
    print("Authenticated to Google Calendar")

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
    task.eventId = event['id']  # Store the event ID in the task object
    db_sessions.commit()  # Save the changes to the database
    print(f"Task added to calendar: {event.get('htmlLink')}")

def sync_calendar_update(task):
    service = authenticate_google_calendar()
    print("Authenticated to Google Calendar")

    if not task.eventId:
        print("No eventId found. Cannot update.")
        return

    updated_event = {
        'summary': task.name,
        'description': task.description,
        'start': {
            'dateTime': task.dueDate.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (task.dueDate + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
    }

    event = service.events().update(
        calendarId='primary',
        eventId=task.eventId,
        body=updated_event
    ).execute()

    print(f"Task updated in calendar: {event.get('htmlLink')}")

def delete_task_from_calendar(task):
    service = authenticate_google_calendar()
    print("Authenticated to Google Calendar")

    if not task.eventId:
        print("No eventId found. Cannot delete.")
        return

    service.events().delete(calendarId='primary', eventId=task.eventId).execute()
    print(f"Task deleted from calendar: {task.eventId}")  # Log the deletion
