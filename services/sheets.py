import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.config import GOOGLE_SHEET_NAME

class GoogleSheetsService:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials/google_creds.json", scope
        )
        client = gspread.authorize(creds)
        self.sheet = client.open(GOOGLE_SHEET_NAME)

    def clean_record(self, record):
        """ניקוי רווחים משמות עמודות"""
        return {key.strip(): value for key, value in record.items()}

    def get_requests(self):
        """קריאה של כל הבקשות של עסקים (Requests)"""
        records = self.sheet.worksheet("Requests").get_all_records()
        return [self.clean_record(r) for r in records]

    def get_suppliers(self):
        """קריאה של כל ההצעות של ספקים (Suppliers)"""
        records = self.sheet.worksheet("Suppliers").get_all_records()
        return [self.clean_record(r) for r in records]

    def add_match(self, match_data):
        """הוספת שורת MATCH לטבלת Matches"""
        self.sheet.worksheet("Matches").append_row(match_data)
