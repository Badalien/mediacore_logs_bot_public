from typing import Any
from googleapiclient.discovery import build
from google.oauth2 import service_account
from pathlib import Path
import logging

parent_directory = str(Path().absolute())

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = parent_directory + '/google_api/google_keys.json'

log_file = parent_directory + '/logs/mc-logs-full.log'
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='[%(asctime)s] {%(name)s}: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger("GOOGLE")

class GoogleClient:

    def __init__(self) -> None:
        self.creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        # The ID of a spreadsheet.
        self.spreadsheet_id = '1lb4cx4KG-7bX55X35zASvaE4KahZjO4CS1TppE4JgNU'
        self.service = None


    def create_service(self):
        if (not self.service):
            self.service = build('sheets', 'v4', credentials=self.creds)

    def read_sheet(self):
        if (not self.service):
            self.create_service()

        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                            range="""LogSource!A10:F14""").execute()

        result = result.get('values', [])
                            
        return result

    def write_sheet(self, support: str, action: str, vendor: str, prior: int, country: str, dp: str, datetime: str) -> Any:
        if (not self.service):
            self.create_service()
        
        

        values = {
            "values":[
                [
                    support,
                    "добавил" if (action == 'insert') else "удалил",
                    vendor,
                    "p={}".format(prior),
                    country,
                    dp,
                    datetime.split("T")[0],
                    datetime.split("T")[1].split(".")[0]
                ]
            ]
        }

        sheet = self.service.spreadsheets()
        request = sheet.values().append(spreadsheetId=self.spreadsheet_id, 
                                range="""LogSource!A1:J1""", valueInputOption="USER_ENTERED", body=values).execute()
        return request
