#!/usr/bin/env python3
"""
Execute the Complete YouTube Outreach Workflow with Email Integration
This runs the full workflow including transcript extraction, email generation, and sending/drafts
"""

import os
import time
import json
import yaml
from dotenv import load_dotenv
from julep import Julep
from google.oauth2 import service_account
from google.auth.transport.requests import Request

load_dotenv()


def get_google_auth_token():
    """Get Google OAuth2 access token from service account"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    try:
        credentials = service_account.Credentials.from_service_account_file(
            'service_account.json',
            scopes=SCOPES
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"❌ Failed to get Google auth token: {e}")
        return None


def create_or_get_task(client, agent_id):
    """Create the complete workflow task or get existing one"""

    # Check if we already have a task ID for the complete workflow
    task_id = os.getenv("COMPLETE_WORKFLOW_TASK_ID")

    # Also check for the basic TASK_ID from our existing workflow
    if not task_id:
        task_id = os.getenv("TASK_ID")

    if task_id:
        try:
            # Verify task exists
            task = client.tasks.get(task_id)
            print(f"✅ Using existing task (ID: {task_id})")
            return task_id
        except:
            print("⚠️ Existing task not found, creating new one...")

    # Load and create new task
    print("\n📄 Loading workflow.yaml...")
    with open('workflow.yaml', 'r') as f:
        task_definition = yaml.safe_load(f)

    print(f"✅ Loaded task: {task_definition['name']}")

    # Create the task
    print("\n🔨 Creating task in Julep...")
    try:
        task = client.tasks.create(
            agent_id=agent_id,
            **task_definition
        )
        print(f"✅ Task created successfully!")
        print(f"   Task ID: {task.id}")

        # Save task ID to .env
        save_task_id_to_env(task.id)

        return task.id

    except Exception as e:
        print(f"❌ Failed to create task: {e}")
        return None


def save_task_id_to_env(task_id):
    """Save task ID to .env file"""

    env_path = '.env'

    # Read current .env content
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Check if key exists and update or append
    key_found = False
    env_key = 'COMPLETE_WORKFLOW_TASK_ID'

    for i, line in enumerate(lines):
        if line.startswith(f'{env_key}='):
            lines[i] = f'{env_key}={task_id}\n'
            key_found = True
            break

    if not key_found:
        lines.append(f'\n{env_key}={task_id}\n')

    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ Saved {env_key} to .env")


def execute_workflow(send_emails=False):
    """Execute the complete YouTube outreach workflow"""

    print("=" * 60)
    print("EXECUTING COMPLETE YOUTUBE OUTREACH WORKFLOW")
    print("=" * 60)

    # Initialize Julep client
    client = Julep(api_key=os.getenv("JULEP_API_KEY"))
    agent_id = os.getenv("AGENT_ID")

    # Get or create task
    task_id = create_or_get_task(client, agent_id)
    if not task_id:
        print("❌ Failed to get task ID")
        return None

    print(f"\n📋 Task ID: {task_id}")

    # Get Google auth token
    print("\n🔑 Getting Google authentication token...")
    google_token = get_google_auth_token()
    if not google_token:
        return None

    print("✅ Google auth token obtained")

    # Prepare execution input
    execution_input = {
        "spreadsheet_id": os.getenv("GOOGLE_SHEET_ID"),
        "google_auth_token": google_token,
        "apify_token": os.getenv("APIFY_TOKEN"),
        "email_address": os.getenv("EMAIL_ADDRESS"),
        "gmail_app_password": os.getenv("GMAIL_APP_PASSWORD"),
        "max_rows": 100,
        "send_emails": send_emails  # Control whether to send or save as drafts
    }

    print(f"\n📊 Configuration:")
    print(f"   Spreadsheet ID: {execution_input['spreadsheet_id']}")
    print(f"   Email Address: {execution_input['email_address']}")
    print(f"   Email Mode: {'SEND EMAILS' if send_emails else 'SAVE AS DRAFTS'}")
    print(f"   Max rows to process: {execution_input['max_rows']}")

    # Confirmation for sending emails
    if send_emails:
        print("\n⚠️  WARNING: Emails will be SENT to recipients!")
        confirm = input("   Type 'yes' to confirm sending emails: ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled - switching to draft mode")
            execution_input['send_emails'] = False

    # Start execution
    print("\n🚀 Starting workflow execution...")
    try:
        execution = client.executions.create(
            task_id=task_id,
            input=execution_input
        )
        print(f"✅ Execution started!")
        print(f"   Execution ID: {execution.id}")

        return execution.id

    except Exception as e:
        print(f"❌ Failed to start execution: {e}")
        return None


def monitor_execution(execution_id):
    """Monitor the execution progress"""

    client = Julep(api_key=os.getenv("JULEP_API_KEY"))

    print("\n⏳ Monitoring execution...")
    print("   (This may take several minutes depending on pending rows)")

    max_wait = 600  # 10 minutes max
    check_interval = 3  # Check every 3 seconds

    for i in range(0, max_wait, check_interval):
        try:
            status = client.executions.get(execution_id)

            elapsed = f"{i}s" if i > 0 else "0s"
            print(f"\r   [{elapsed}] Status: {status.status}", end="", flush=True)

            if status.status == "succeeded":
                print(" ✅")
                print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")

                if hasattr(status, 'output'):
                    output = status.output
                    print("\n📊 Results:")
                    if isinstance(output, dict):
                        print(f"   Total rows checked: {output.get('total_rows_checked', 'N/A')}")
                        print(f"   Pending rows found: {output.get('pending_rows_found', 'N/A')}")
                        print(f"   Rows processed: {output.get('rows_processed', 'N/A')}")
                        print(f"   Email mode: {output.get('email_mode', 'N/A')}")

                        # Print the report if available
                        if 'report' in output:
                            print("\n📝 Detailed Report:")
                            print(output['report'])

                return True

            elif status.status == "failed":
                print(" ❌")
                print("\n❌ WORKFLOW FAILED!")

                if hasattr(status, 'error'):
                    print(f"\nError: {status.error}")

                if hasattr(status, 'output'):
                    print(f"\nOutput: {status.output}")

                return False

            elif status.status in ["cancelled", "stopped"]:
                print(f" ⚠️ {status.status}")
                return False

            time.sleep(check_interval)

        except Exception as e:
            print(f"\n❌ Error checking status: {e}")
            return False

    print("\n⚠️ Execution timed out after 10 minutes")
    print("   Check Julep dashboard for status")
    return False


def main():
    """Main execution"""

    # Check for required environment variables
    required_vars = [
        'JULEP_API_KEY', 'AGENT_ID', 'APIFY_TOKEN',
        'GOOGLE_SHEET_ID', 'EMAIL_ADDRESS', 'GMAIL_APP_PASSWORD'
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return

    print("\n📧 Email Mode Selection:")
    print("1. Save as DRAFTS (recommended for testing)")
    print("2. SEND emails to recipients")

    choice = input("\nSelect mode (1 or 2): ").strip()
    send_emails = (choice == "2")

    # Execute the workflow
    execution_id = execute_workflow(send_emails=send_emails)

    if execution_id:
        # Monitor the execution
        success = monitor_execution(execution_id)

        if success:
            print("\n✅ Next steps:")
            if send_emails:
                print("1. Check your Gmail sent folder for confirmation")
                print("2. Monitor recipient responses")
            else:
                print("1. Check Google Sheet columns E-F for email drafts")
                print("2. Review and manually send emails when ready")

            print("3. Update sheet with response tracking")
            print("4. Follow up with engaged recipients")
        else:
            print("\n💡 Troubleshooting:")
            print("1. Check if sheet is shared with service account")
            print("2. Verify APIFY token is valid")
            print("3. Check email credentials")
            print("4. Review Julep dashboard for detailed logs")

        print(f"\n📊 View execution details at:")
        print(f"   https://dashboard.julep.ai/executions/{execution_id}")


if __name__ == "__main__":
    main()