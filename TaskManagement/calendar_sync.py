import datetime  # Import datetime
import os.path
from flask import session, url_for, redirect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from TaskManagement.database import db_sessions 
import sys
import os 
import json
from TaskManagement.models import User
from flask_login import current_user
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Key for encryption and decryption
# fernet_key = Fernet.generate_key()

# Instance the Fernet class with the key
load_dotenv(dotenv_path="fernet.env") # Load environment variables from your .env file
fernet_key = os.environ.get('FERNET_SECRET_KEY')
fernet = Fernet(fernet_key)
# print("Key generated for encryption:", fernet_key)

# If modifying these SCOPES, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']
# REDIRECT_URI = 'https://task-management-software-1aqw.onrender.com/authorize-redirect'
REDIRECT_URI = 'http://localhost:5000/authorize-redirect'

def is_user_google_authed(user):
    if not user.google_token_json:
        print("User does not have a Google token JSON.")
        return False
    try:
        token = fernet.decrypt(user.google_token_json.encode()).decode()
        creds = Credentials.from_authorized_user_info(json.loads(token), SCOPES)
        return creds and creds.valid
    except Exception:
        print("User's Google token JSON is invalid or could not be decrypted.")
        return redirect(url_for('task.dashboard'))  # Redirect to login if token is invalid



def generate_auth_url():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['oauth_state'] = state
    return auth_url

def fetch_and_store_token(code, state, user):
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    token = creds.to_json()
    # Encrypt the token before storing it
    encToken = fernet.encrypt(token.encode())
    
    user.google_token_json = encToken
    db_sessions.commit()

def authenticate_google_calendar(curr_user):
    creds = None

    if is_user_google_authed(curr_user):
        encToken = curr_user.google_token_json
        if isinstance(encToken, str):
            encToken = encToken.encode()
        token = fernet.decrypt(encToken).decode()
        creds = Credentials.from_authorized_user_info(json.loads(token), SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            token = creds.to_json()
            encToken = fernet.encrypt(token.encode())
            curr_user.google_token_json = encToken
            db_sessions.commit()
    else:
        # If not authed or can't refresh, prompt OAuth again
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        # Save new token
        token = creds.to_json()
        encToken = fernet.encrypt(token.encode())
        curr_user.google_token_json = encToken
        db_sessions.commit()

    return build('calendar', 'v3', credentials=creds)

# def authenticate_google_calendar(curr_user):
#     creds = None
#     if curr_user.google_token_json:
#         # Decode the encrypted token
#         encToken = curr_user.google_token_json
#         if isinstance(encToken, str):
#             encToken = encToken.encode()
#         token = fernet.decrypt(encToken).decode()
#         # Load the token into credentials
#         creds = Credentials.from_authorized_user_info(json.loads(token), SCOPES)
#         # creds = Credentials.from_authorized_user_info(json.loads(current_user.google_token_json), SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save encoded token back to user
#         token = creds.to_json()
#         encToken = fernet.encrypt(token.encode())
#         curr_user.google_token_json = encToken
#         # Save the encrypted token to the database
#         # db_sessions.query(User).filter_by(id=current_user.id).update({"google_token_json": encToken})
#         # current_user.google_token_json = creds.to_json()
#         db_sessions.commit()
#     return build('calendar', 'v3', credentials=creds)


def add_task_to_calendar(task, task_title, task_description, task_due_date):
    """Add a task to Google Calendar."""
    service = authenticate_google_calendar(current_user)
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
    # event = service.events().insert(calendarId='primary', body=event).execute()
    event = service.events().insert(calendarId="primary", body=event).execute()
    task.eventId = event['id']  # Store the event ID in the task object
    db_sessions.commit()  # Save the changes to the database
    print(f"Task added to calendar: {event.get('htmlLink')}")

def sync_calendar_update(task):
    service = authenticate_google_calendar(current_user)
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
    service = authenticate_google_calendar(current_user)
    print("Authenticated to Google Calendar")
    if not task.eventId:
        print("No eventId found. Cannot delete.")
        return
    service.events().delete(calendarId='primary', eventId=task.eventId).execute()
    print(f"Task deleted from calendar: {task.eventId}")  # Log the deletion



# def authenticate_google_calendar(current_user):
#     creds = None

#     if current_user.google_token_json:
#         creds = Credentials.from_authorized_user_info(json.loads(current_user.google_token_json), SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)

#         # Save token back to user
#         current_user.google_token_json = creds.to_json()
#         db_sessions.commit()

#     return build('calendar', 'v3', credentials=creds)

# def authenticate_google_calendar():
#     """Authenticate and return the Google Calendar service."""
#     creds = None
#     # Check if token.json exists (stores user's access and refresh tokens)
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If no valid credentials, authenticate the user
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for future use
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     return build('calendar', 'v3', credentials=creds)


# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
#     return os.path.join(base_path, relative_path)


# def authenticate_google_calendar():
    # """Authenticate and return the Google Calendar service."""
    # creds = None

    # # Save token.json in a writable location (user folder or project root in dev)
    # if getattr(sys, 'frozen', False):
    #     # App is frozen (running as .exe)
    #     base_path = os.path.dirname(sys.executable)
    # else:
    #     # Running normally (in dev mode)
    #     base_path = os.path.dirname(__file__)

    # # user_data_dir = os.path.join(base_path, "TaskManagement")
    # user_data_dir = base_path
    # os.makedirs(user_data_dir, exist_ok=True)
    # token_path = os.path.join(user_data_dir, "token.json")
    # # credentials_path = os.path.join(user_data_dir, "credentials.json")
    # credentials_path = resource_path("credentials.json")


    # # Check if the credentials file exists before continuing
    # if not os.path.exists(credentials_path):
    #     raise FileNotFoundError(f"credentials.json not found at {credentials_path}")

    # if os.path.exists(token_path):
    #     creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # # If no valid credentials, authenticate the user
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             credentials_path, SCOPES)
    #         creds = flow.run_local_server(port=0)
        
    #     with open(token_path, 'w') as token:
    #         token.write(creds.to_json())
    
    # return build('calendar', 'v3', credentials=creds)

# def authenticate_google_calendar():
#     """Authenticate and return the Google Calendar service."""
#     creds = None

#     # Save token.json in a writable location (user folder or project root in dev)
#     if getattr(sys, 'frozen', False):
#         # App is frozen (running as .exe)
#         base_path = os.path.dirname(sys.executable)
#     else:
#         # Running normally (in dev mode)
#         base_path = os.path.dirname(__file__)

#     user_data_dir = os.path.join(base_path, "TaskManagement")
#     # user_data_dir = os.path.join(os.path.dirname(__file__), "TaskManagement")
#     # user_data_dir = os.path.expanduser("~/.Task Management Software")
#     os.makedirs(user_data_dir, exist_ok=True)
#     token_path = os.path.join(user_data_dir, "token.json")


#     # Check if token.json exists (stores user's access and refresh tokens)
#     # token_path = resource_path("TaskManagement/token.json")
#     # if os.path.exists('token.json'):
#     if os.path.exists(token_path):
#         # creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#         creds = Credentials.from_authorized_user_file(token_path, SCOPES)
#     # If no valid credentials, authenticate the user
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             # flow = InstalledAppFlow.from_client_secrets_file(
#             #     'credentials.json', SCOPES)
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 resource_path("TaskManagement/credentials.json"), SCOPES)

#             creds = flow.run_local_server(port=0)
#         # Save the credentials for future use
#         with open(token_path, 'w') as token:
#             token.write(creds.to_json())
#     return build('calendar', 'v3', credentials=creds)

# try:
#     service = authenticate_google_calendar()  # Use the function to get the service object

#     now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

#     event_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
#     events = event_result.get('items', [])

#     if not events:
#         print('No upcoming events found.')

#     for event in events:
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         print(start, event['summary'])

# except HttpError as error:
#     # Handle errors from the API
#     print('An error occurred:', error)

# def add_task_to_calendar(task, task_title, task_description, task_due_date):
#     """Add a task to Google Calendar."""
#     service = authenticate_google_calendar(current_user)
#     print("Authenticated to Google Calendar")

#     # Create an event
#     event = {
#         'summary': task_title,
#         'description': task_description,
#         'start': {
#             'dateTime': task_due_date.isoformat(),
#             'timeZone': 'UTC',
#         },
#         'end': {
#             'dateTime': (task_due_date + datetime.timedelta(hours=1)).isoformat(),
#             'timeZone': 'UTC',
#         },
#     }

#     # Insert the event into the user's calendar
#     # event = service.events().insert(calendarId='primary', body=event).execute()
#     event = service.events().insert(calendarId="primary", body=event).execute()

#     task.eventId = event['id']  # Store the event ID in the task object
#     db_sessions.commit()  # Save the changes to the database
#     print(f"Task added to calendar: {event.get('htmlLink')}")

# def sync_calendar_update(task):
#     service = authenticate_google_calendar(current_user)
#     print("Authenticated to Google Calendar")

#     if not task.eventId:
#         print("No eventId found. Cannot update.")
#         return

#     updated_event = {
#         'summary': task.name,
#         'description': task.description,
#         'start': {
#             'dateTime': task.dueDate.isoformat(),
#             'timeZone': 'UTC',
#         },
#         'end': {
#             'dateTime': (task.dueDate + datetime.timedelta(hours=1)).isoformat(),
#             'timeZone': 'UTC',
#         },
#     }

#     event = service.events().update(
#         calendarId='primary',
#         eventId=task.eventId,
#         body=updated_event
#     ).execute()

#     print(f"Task updated in calendar: {event.get('htmlLink')}")

# def delete_task_from_calendar(task):
#     service = authenticate_google_calendar(current_user)
#     print("Authenticated to Google Calendar")

#     if not task.eventId:
#         print("No eventId found. Cannot delete.")
#         return

#     service.events().delete(calendarId='primary', eventId=task.eventId).execute()
#     print(f"Task deleted from calendar: {task.eventId}")  # Log the deletion
