import os, logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
ROSTER_SPREADSHEET_ID = "1ODzv8_SvVdeMWoHXGIbU50v7yeVz9Gvtn0K7TNTKGes"
RANGE_NAME = 'Contact!A3:M62'

def pull_sheet_data():
    contact_data = {}
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google-credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])
        for row in values:
            full_name = row[1] + " " + row[0]
            phone = row[2]
            email = row[4]
            birthday = row[11]
            info = {"phone": phone, "email": email, "birthday": birthday}
            contact_data[full_name] = info

    except HttpError as err:
        logging.error(f"HTTP Error occured while parsing sheet data: {err}")

    return contact_data
