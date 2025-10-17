#!/usr/bin/env python3
"""
Python orchestrator for YouTube outreach
Uses simple Julep tasks for each video
"""

import os
import time
import yaml
from dotenv import load_dotenv
from julep import Julep
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()


def get_google_auth():
    """Get Google Sheets service"""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    credentials = service_account.Credentials.from_service_account_file(
        'service_account.json',
        scopes=SCOPES
    )

    return build('sheets', 'v4', credentials=credentials)


def read_google_sheet(service, spreadsheet_id):
    """Read data from Google Sheet"""
    range_name = 'A1:F100'

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])
        return values
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")
        return []


def update_sheet_row(service, spreadsheet_id, row_number, status, email_subject, email_body):
    """Update a single row in the sheet"""
    range_name = f'D{row_number}:F{row_number}'
    # Ensure email_body and subject are strings
    subject_str = str(email_subject) if email_subject else ""
    body_str = str(email_body)[:500] if email_body else ""
    values = [[status, subject_str, body_str]]

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
        print(f"✅ Updated row {row_number}")
    except Exception as e:
        print(f"❌ Error updating row {row_number}: {e}")


def create_single_video_task(client, agent_id):
    """Create the single video processing task"""

    # Load task definition
    with open('single_video_task.yaml', 'r') as f:
        task_definition = yaml.safe_load(f)

    try:
        task = client.tasks.create(
            agent_id=agent_id,
            **task_definition
        )
        print(f"✅ Created task: {task.name} (ID: {task.id})")
        return task.id
    except Exception as e:
        print(f"❌ Failed to create task: {e}")
        return None


def process_single_video(client, task_id, youtube_url, creator_name):
    """Process a single video using Julep task"""

    print(f"\n📺 Processing video for {creator_name}...")
    print(f"   URL: {youtube_url}")

    try:
        # Start execution
        execution = client.executions.create(
            task_id=task_id,
            input={
                "youtube_url": youtube_url,
                "creator_name": creator_name,
                "apify_token": os.getenv("APIFY_TOKEN")
            }
        )

        print(f"   Execution started: {execution.id}")

        # Wait for completion (max 60 seconds)
        for i in range(60):
            status = client.executions.get(execution.id)

            if status.status == "succeeded":
                print(f"   ✅ Completed successfully!")

                if hasattr(status, 'output'):
                    return {
                        "success": True,
                        "email_subject": status.output.get('email_subject', ''),
                        "email_body": status.output.get('email_body', ''),
                        "video_title": status.output.get('video_title', '')
                    }

            elif status.status == "failed":
                error_msg = getattr(status, 'error', 'Unknown error')
                print(f"   ❌ Failed: {error_msg}")
                # Print full status object for debugging
                print(f"   Debug - Full status: {status}")
                return {"success": False, "error": str(error_msg)}

            time.sleep(1)

        print(f"   ⚠️ Timeout after 60 seconds")
        return {"success": False, "error": "Timeout"}

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Main orchestration logic"""

    print("=" * 60)
    print("YOUTUBE OUTREACH ORCHESTRATOR")
    print("=" * 60)

    # Initialize services
    print("\n🔧 Initializing services...")
    sheets_service = get_google_auth()
    julep_client = Julep(api_key=os.getenv("JULEP_API_KEY"))
    agent_id = os.getenv("AGENT_ID")
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

    # Create Julep task
    print("\n📋 Creating Julep task...")
    task_id = create_single_video_task(julep_client, agent_id)
    if not task_id:
        print("❌ Failed to create task. Exiting.")
        return

    # Read Google Sheet
    print("\n📊 Reading Google Sheet...")
    sheet_data = read_google_sheet(sheets_service, spreadsheet_id)

    if not sheet_data or len(sheet_data) < 2:
        print("❌ No data found in sheet")
        return

    headers = sheet_data[0]
    data_rows = sheet_data[1:]

    # Find pending rows
    pending_rows = []
    for idx, row in enumerate(data_rows):
        row_number = idx + 2  # Account for header and 1-based indexing

        if len(row) >= 3:  # Has at least name, URL, email
            status = row[3] if len(row) > 3 else ""

            if status.lower() == "pending" or status == "":
                pending_rows.append({
                    "row_number": row_number,
                    "creator_name": row[0],
                    "youtube_url": row[1],
                    "email": row[2]
                })

    print(f"✅ Found {len(pending_rows)} pending rows")

    if not pending_rows:
        print("No pending rows to process")
        return

    # Process each pending row
    print(f"\n🚀 Processing {len(pending_rows)} videos...")
    print("=" * 60)

    successful = 0
    failed = 0

    for row in pending_rows:
        # Update status to Processing
        update_sheet_row(
            sheets_service,
            spreadsheet_id,
            row['row_number'],
            "Processing",
            "Fetching transcript...",
            ""
        )

        # Process video
        result = process_single_video(
            julep_client,
            task_id,
            row['youtube_url'],
            row['creator_name']
        )

        # Update sheet with results
        if result['success']:
            update_sheet_row(
                sheets_service,
                spreadsheet_id,
                row['row_number'],
                "Draft Ready",
                result['email_subject'],
                result['email_body']
            )
            successful += 1
        else:
            update_sheet_row(
                sheets_service,
                spreadsheet_id,
                row['row_number'],
                "Failed",
                "Error",
                result.get('error', 'Unknown error')
            )
            failed += 1

        # Small delay between requests
        time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📝 Total processed: {successful + failed}")
    print("\n✅ Next steps:")
    print("1. Check your Google Sheet columns D-F for email drafts")
    print("2. Review and send emails manually")
    print("3. Update sheet with response tracking")


if __name__ == "__main__":
    main()