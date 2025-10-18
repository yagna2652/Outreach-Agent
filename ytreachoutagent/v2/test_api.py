#!/usr/bin/env python3
"""
Test script for API call tasks
"""

import os
import json
from dotenv import load_dotenv
from julep import Julep

# Load environment variables
load_dotenv()

def test_simple_api():
    """Test the simple API call task"""

    # Initialize Julep client
    client = Julep(api_key=os.getenv("JULEP_API_KEY"))

    # Get or create agent
    agent_id = os.getenv("YOUTUBE_MONITOR_AGENT_ID")
    if agent_id:
        try:
            agent = client.agents.get(agent_id)
            print(f"✅ Using existing agent: {agent_id}")
        except:
            print("❌ Agent not found")
            return
    else:
        print("❌ No agent ID found. Run 'python agents/youtube_monitor_agent.py' first")
        return

    # Load test task
    import yaml
    task_file = "tasks/test/test_no_input.yaml"  # Testing without input
    with open(task_file, "r") as f:
        task_def = yaml.safe_load(f)
    print(f"   Using task file: {task_file}")

    # Register the test task
    print("\n📝 Registering test task...")
    try:
        task = client.tasks.create(
            agent_id=agent_id,
            **task_def
        )
        print(f"✅ Task registered: {task.id}")
    except Exception as e:
        print(f"❌ Failed to register task: {e}")
        return

    # Test input data - adjust based on task file
    if "no_input" in task_file:
        test_input = {}
    elif "hardcoded" in task_file:
        test_input = {"test": "dummy"}
    else:
        test_input = {
            "spreadsheet_id": os.getenv("GOOGLE_SPREADSHEET_ID"),
            "google_auth_token": os.getenv("GOOGLE_AUTH_TOKEN")
        }

        # Check if we have the required credentials
        if not test_input["spreadsheet_id"] or not test_input["google_auth_token"]:
            print("\n⚠️  Missing credentials in .env file:")
            if not test_input["spreadsheet_id"]:
                print("   - GOOGLE_SPREADSHEET_ID")
            if not test_input["google_auth_token"]:
                print("   - GOOGLE_AUTH_TOKEN")
            print("\n📝 To get Google Auth Token:")
            print("   1. Go to: https://developers.google.com/oauthplayground/")
            print("   2. Select 'Google Sheets API v4'")
            print("   3. Click 'Authorize APIs'")
            print("   4. Click 'Exchange authorization code for tokens'")
            print("   5. Copy the 'Access token' to your .env file as GOOGLE_AUTH_TOKEN")
            return

    # Execute the task
    print("\n🚀 Executing test task...")
    try:
        execution = client.executions.create(
            task_id=task.id,
            input=test_input
        )
        print(f"✅ Execution started: {execution.id}")

        # Wait for completion (simplified polling)
        import time
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            exec_status = client.executions.get(execution.id)

            if hasattr(exec_status, 'status'):
                status = exec_status.status
            else:
                status = 'running'

            if status in ['completed', 'failed']:
                print(f"\n📊 Execution {status}")

                # Try to get output
                if hasattr(exec_status, 'output'):
                    print(f"Output: {json.dumps(exec_status.output, indent=2)}")

                if status == 'failed' and hasattr(exec_status, 'error'):
                    print(f"Error: {exec_status.error}")

                break

            if i % 5 == 0:
                print(f"   ... waiting ({i}s)")

    except Exception as e:
        print(f"❌ Execution failed: {e}")


if __name__ == "__main__":
    test_simple_api()