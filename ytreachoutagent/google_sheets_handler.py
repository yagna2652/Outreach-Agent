#!/usr/bin/env python3
"""
Google Sheets Handler - Clean implementation using service account
"""

import os
import json
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from julep import Julep
from dotenv import load_dotenv

load_dotenv()


class GoogleSheetsHandler:
    """Handler for Google Sheets operations using Julep and service account"""

    def __init__(self):
        """Initialize the handler with credentials and client"""
        self.julep_client = Julep(api_key=os.getenv("JULEP_API_KEY"))
        self.agent_id = os.getenv("AGENT_ID")
        self.spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

        # Setup Google Sheets authentication
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = service_account.Credentials.from_service_account_file(
            'service_account.json',
            scopes=self.SCOPES
        )

    def get_access_token(self) -> str:
        """Get a fresh access token"""
        self.credentials.refresh(Request())
        return self.credentials.token

    def read_sheet(self, range_name: str = "A1:F100") -> Dict[str, Any]:
        """
        Read data from the Google Sheet

        Args:
            range_name: A1 notation of the range to read

        Returns:
            Dict containing the sheet data
        """
        access_token = self.get_access_token()
        read_url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{range_name}"

        task_yaml = f"""
name: Read Google Sheet
description: Read data from Google Sheet

tools:
- name: sheets_reader
  type: api_call
  api_call:
    method: GET
    url: "{read_url}"
    headers:
      Authorization: "Bearer {access_token}"

main:
- tool: sheets_reader
- return:
    data: ${{{{ steps[0].output.json }}}}
"""

        # Create and execute task
        task = self.julep_client.tasks.create(
            agent_id=self.agent_id,
            **yaml.safe_load(task_yaml)
        )

        execution = self.julep_client.executions.create(
            task_id=task.id,
            input={}
        )

        # Wait for completion
        return self._wait_for_execution(execution.id)

    def write_sheet(self, range_name: str, values: List[List[str]]) -> Dict[str, Any]:
        """
        Write data to the Google Sheet

        Args:
            range_name: A1 notation of the range to write
            values: 2D array of values to write

        Returns:
            Dict containing the write response
        """
        access_token = self.get_access_token()
        write_url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{range_name}?valueInputOption=RAW"

        write_data = {"values": values}

        task_yaml = f"""
name: Write to Google Sheet
description: Write data to Google Sheet

tools:
- name: sheets_writer
  type: api_call
  api_call:
    method: PUT
    url: "{write_url}"
    headers:
      Authorization: "Bearer {access_token}"
      Content-Type: application/json
    json_body: {json.dumps(write_data)}

main:
- tool: sheets_writer
- return:
    data: ${{{{ steps[0].output.json }}}}
"""

        # Create and execute task
        task = self.julep_client.tasks.create(
            agent_id=self.agent_id,
            **yaml.safe_load(task_yaml)
        )

        execution = self.julep_client.executions.create(
            task_id=task.id,
            input={}
        )

        # Wait for completion
        return self._wait_for_execution(execution.id)

    def update_row_status(self, row_number: int, status: str, notes: str = "") -> Dict[str, Any]:
        """
        Update the status of a specific row

        Args:
            row_number: The row number to update (1-based)
            status: New status value
            notes: Additional notes

        Returns:
            Dict containing the update response
        """
        # Assuming Status is in column D and Notes in column E
        range_name = f"D{row_number}:E{row_number}"
        values = [[status, notes]]

        return self.write_sheet(range_name, values)

    def get_pending_rows(self) -> List[Dict[str, Any]]:
        """
        Get all rows with 'Pending' status

        Returns:
            List of dicts with row data
        """
        data = self.read_sheet()

        if not data:
            return []

        # Handle string response (might be JSON string)
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except:
                return []

        if 'values' not in data:
            return []

        rows = data['values']
        if len(rows) <= 1:  # Only headers or empty
            return []

        headers = rows[0]
        pending_rows = []

        for i, row in enumerate(rows[1:], start=2):  # Start from row 2 (after headers)
            if len(row) > 3 and row[3].lower() == 'pending':  # Status is in column D (index 3)
                row_dict = {
                    'row_number': i,
                    'creator_name': row[0] if len(row) > 0 else '',
                    'channel_url': row[1] if len(row) > 1 else '',
                    'recipient_email': row[2] if len(row) > 2 else '',
                    'status': row[3] if len(row) > 3 else '',
                    'notes': row[4] if len(row) > 4 else ''
                }
                pending_rows.append(row_dict)

        return pending_rows

    def _wait_for_execution(self, execution_id: str, max_wait: int = 30) -> Optional[Dict[str, Any]]:
        """
        Wait for execution to complete and return the result

        Args:
            execution_id: The execution ID to wait for
            max_wait: Maximum seconds to wait

        Returns:
            The execution output or None if failed
        """
        import time

        for _ in range(max_wait):
            status = self.julep_client.executions.get(execution_id)

            if status.status == "succeeded":
                if hasattr(status, 'output'):
                    # Extract data from the return statement
                    output = status.output
                    if isinstance(output, dict) and 'data' in output:
                        data = output['data']
                        # Handle Julep's template string format
                        if isinstance(data, str) and data.startswith("${'"):
                            # Extract the dict part from the template string
                            try:
                                # Remove the ${ prefix and ' suffix
                                json_str = data[2:-1] if data.endswith("'}") else data[2:]
                                # Replace single quotes with double quotes for JSON
                                json_str = json_str.replace("'", '"')
                                import json
                                return json.loads(json_str)
                            except:
                                return data
                        return data
                    return output
                return {"status": "success"}

            elif status.status == "failed":
                print(f"Execution failed: {status.error if hasattr(status, 'error') else 'Unknown error'}")
                return None

            time.sleep(1)

        print(f"Execution timed out after {max_wait} seconds")
        return None


# Example usage
if __name__ == "__main__":
    handler = GoogleSheetsHandler()

    print("Testing Google Sheets Handler...")
    print("=" * 50)

    # Test reading
    print("\n1. Reading sheet data...")
    data = handler.read_sheet("A1:F5")
    if data:
        # Handle both dict and string responses
        if isinstance(data, str):
            print(f"✅ Successfully read data (raw response)")
            print(f"   Response type: {type(data)}")
            print(f"   First 200 chars: {data[:200]}")
        elif isinstance(data, dict):
            print(f"✅ Successfully read {len(data.get('values', []))} rows")
            if 'values' in data:
                for row in data['values'][:2]:  # Show first 2 rows
                    print(f"   {row}")

    # Test getting pending rows
    print("\n2. Getting pending rows...")
    pending = handler.get_pending_rows()
    print(f"✅ Found {len(pending)} pending rows")
    for row in pending:
        print(f"   Row {row['row_number']}: {row['creator_name']} - {row['channel_url']}")

    # Test writing (optional)
    # print("\n3. Testing write...")
    # result = handler.update_row_status(2, "Processed", f"Tested at {datetime.now().isoformat()}")
    # if result:
    #     print(f"✅ Successfully updated row 2")

    print("\n" + "=" * 50)
    print("✅ Google Sheets Handler is ready!")