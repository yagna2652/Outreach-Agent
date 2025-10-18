#!/usr/bin/env python3
"""
Test writing to Google Sheets
"""

import os
import sys
import yaml
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from julep import Julep
from google.oauth2 import service_account
from google.auth.transport.requests import Request

load_dotenv()

print("=" * 60)
print("GOOGLE SHEETS WRITE TEST")
print("=" * 60)

# Get service account credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(
    'service_account.json',
    scopes=SCOPES
)
credentials.refresh(Request())
access_token = credentials.token

# Initialize Julep client
client = Julep(api_key=os.getenv("JULEP_API_KEY"))
agent_id = os.getenv("AGENT_ID")
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

print(f"\n📋 Sheet ID: {spreadsheet_id}")
print(f"🤖 Agent ID: {agent_id}")

# Prepare the data to write
timestamp = datetime.now().isoformat()
write_data = {
    "values": [
        ["Test Write", timestamp, "Success", "Working!"]
    ]
}

# Create URLs and headers
write_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A3:D3?valueInputOption=RAW"
auth_header = f"Bearer {access_token}"

task_yaml = f"""
name: Sheets Write Test
description: Test writing to Google Sheets

tools:
- name: sheets_writer
  type: api_call
  api_call:
    method: PUT
    url: "{write_url}"
    headers:
      Authorization: "{auth_header}"
      Content-Type: application/json
    json_body: {json.dumps(write_data)}

main:
- tool: sheets_writer

- return:
    status: "success"
    response: ${{{{ steps[0].output }}}}
"""

print("\n📝 Creating write task...")
try:
    task = client.tasks.create(
        agent_id=agent_id,
        **yaml.safe_load(task_yaml)
    )
    print(f"✅ Task created: {task.id}")
except Exception as e:
    print(f"❌ Failed to create task: {e}")
    sys.exit(1)

print("\n🚀 Running execution...")
try:
    execution = client.executions.create(
        task_id=task.id,
        input={}
    )
    print(f"✅ Execution started: {execution.id}")
except Exception as e:
    print(f"❌ Failed to start execution: {e}")
    sys.exit(1)

print("\n⏳ Waiting for execution to complete...")
max_wait = 30
success = False

for i in range(max_wait):
    try:
        status = client.executions.get(execution.id)

        print(f"   [{i+1}/{max_wait}] Status: {status.status}", end="")

        if status.status == "succeeded":
            print(" ✅")
            print("\n🎉 SUCCESS! Writing to Google Sheets is working!")
            success = True

            if hasattr(status, 'output'):
                output = status.output
                print("\n📊 Write Response:")
                if isinstance(output, dict) and 'response' in output:
                    response = output['response']
                    if isinstance(response, dict) and 'json' in response:
                        json_resp = response['json']
                        print(f"  Updated range: {json_resp.get('updatedRange', 'N/A')}")
                        print(f"  Updated rows: {json_resp.get('updatedRows', 'N/A')}")
                        print(f"  Updated columns: {json_resp.get('updatedColumns', 'N/A')}")
                        print(f"  Updated cells: {json_resp.get('updatedCells', 'N/A')}")
                    else:
                        print(json.dumps(response, indent=2)[:500])
                else:
                    print(json.dumps(output, indent=2)[:500])

            print("\n✅ Data written to sheet:")
            print(f"  Row 3: {write_data['values'][0]}")
            break

        elif status.status == "failed":
            print(" ❌")
            print("\n❌ Execution failed!")

            if hasattr(status, 'error'):
                print(f"Error: {status.error}")

            if hasattr(status, 'output'):
                print(f"Output: {status.output}")

            break

        else:
            print(f" ({status.status})")

        time.sleep(1)

    except Exception as e:
        print(f"\n❌ Error checking status: {e}")
        break

if success:
    print("\n✅ Google Sheets Integration Complete!")
    print("1. ✅ Reading from sheet works")
    print("2. ✅ Writing to sheet works")
    print("3. Ready to integrate with full workflow!")
    print("\nCheck your Google Sheet - row 3 should have test data!")
else:
    print("\n❌ Write test failed")

print("\n" + "=" * 60)