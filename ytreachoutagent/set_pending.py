#!/usr/bin/env python3
"""
Set a row to Pending status for testing
"""

import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()


def main():
    """Set row 2 to Pending status"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    credentials = service_account.Credentials.from_service_account_file(
        'service_account.json',
        scopes=SCOPES
    )

    service = build('sheets', 'v4', credentials=credentials)
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

    # Update row 2 column D to "Pending"
    range_name = 'D2'
    values = [["Pending"]]

    body = {
        'values': values
    }

    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        print("✅ Set row 2 (MKBHD) status to 'Pending'")
        print("   Ready to test the orchestrator!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()