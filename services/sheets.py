import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsService:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if creds_json is None:
            raise Exception("❌ לא נמצא משתנה סביבה GOOGLE_CREDENTIALS_JSON")

        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sheet_name = os.getenv("GOOGLE_SHEET_NAME")
        if not sheet_name:
            raise Exception("❌ לא הוגדר GOOGLE_SHEET_NAME")
        self.sheet = client.open(sheet_name)

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
