#!/usr/bin/env python3
"""
Simple test of Google Sheets API with proper header formatting
"""

import os
import sys
import yaml
import time
import json
from dotenv import load_dotenv
from julep import Julep
from google.oauth2 import service_account
from google.auth.transport.requests import Request

load_dotenv()

print("=" * 60)
print("SIMPLE GOOGLE SHEETS API TEST")
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
print(f"🔑 Access token: {access_token[:50]}...")

# Create a simple task that just reads from the sheet
# We'll construct the full URL and header as strings to avoid template issues
read_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A1:F10"
auth_header = f"Bearer {access_token}"

task_yaml = f"""
name: Simple Sheets Read Test
description: Simple test to read from Google Sheets

tools:
- name: sheets_reader
  type: api_call
  api_call:
    method: GET
    url: "{read_url}"
    headers:
      Authorization: "{auth_header}"

main:
- tool: sheets_reader

- return:
    status: "success"
    data: ${{{{ steps[0].output }}}}
"""

print("\n📝 Creating simple read task...")
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
            print("\n🎉 SUCCESS! Google Sheets API is working!")
            success = True

            if hasattr(status, 'output'):
                output = status.output
                print("\n📊 Sheet Data:")
                if isinstance(output, dict) and 'data' in output:
                    data = output['data']
                    if isinstance(data, dict) and 'values' in data:
                        values = data['values']
                        for row in values[:5]:  # Show first 5 rows
                            print(f"  {row}")
                        if len(values) > 5:
                            print(f"  ... and {len(values) - 5} more rows")
                    else:
                        print(json.dumps(data, indent=2)[:500])
                else:
                    print(json.dumps(output, indent=2)[:500])
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
    print("\n✅ Next Steps:")
    print("1. Google Sheets reading is working!")
    print("2. Now we can test writing to the sheet")
    print("3. Then integrate with the full workflow")
else:
    print("\n❌ Google Sheets integration failed")
    print("Check the debug output above for details")

print("\n" + "=" * 60)