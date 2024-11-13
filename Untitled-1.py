import os
import pickle
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  # or 'calendar' for full access

def authenticate_google_account():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def get_calendar_events(service, max_results=10):
    events_result = service.events().list(calendarId='primary', timeMin='2024-01-01T00:00:00Z',
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()

    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")

def create_event(service, summary, start_time, end_time):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {created_event['htmlLink']}")

def main():
    # Authenticate and get the Google Calendar service
    service = authenticate_google_account()

    # Example event details
    summary = 'Practice Google Calendar Event'
    start_time = datetime.now() + timedelta(days=1)  # Start time 1 day from now
    end_time = start_time + timedelta(hours=1)       # End time 1 hour later

    # Create the event
    create_event(service, summary, start_time, end_time)

if __name__ == '__main__':
    main()