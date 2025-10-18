#!/usr/bin/env python3
"""
Simplified Julep-native YouTube Outreach Agent
Using synchronous Julep client
"""

import os
import time
import sys
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


def start_youtube_agent(mode="monitor", send_emails=False):
    """
    Start the YouTube outreach agent

    Modes:
    - monitor: Start and monitor with status checks
    - fire_and_forget: Start and exit (agent continues on Julep)
    """

    print("=" * 60)
    print("🤖 JULEP-NATIVE YOUTUBE OUTREACH AGENT")
    print("=" * 60)
    print("Let Julep handle the orchestration!\n")

    # Initialize Julep client
    client = Julep(api_key=os.getenv("JULEP_API_KEY"))
    agent_id = os.getenv("AGENT_ID")

    # Try to find the workflow task ID
    task_id = os.getenv("WORKFLOW_TASK_ID")  # Created by create_tasks.py
    if not task_id:
        task_id = os.getenv("COMPLETE_WORKFLOW_TASK_ID")  # From run_workflow.py
    if not task_id:
        task_id = os.getenv("TASK_ID")  # Fallback to original

    if not task_id:
        print("❌ No workflow task ID found in .env")
        print("   Run create_tasks.py first to create the workflow task")
        return None

    print(f"📋 Using task ID: {task_id}")

    # Get Google auth token
    print("🔑 Getting Google authentication...")
    google_token = get_google_auth_token()
    if not google_token:
        return None

    # Prepare input for the workflow
    workflow_input = {
        "spreadsheet_id": os.getenv("GOOGLE_SHEET_ID"),
        "google_auth_token": google_token,
        "apify_token": os.getenv("APIFY_TOKEN"),
        "email_address": os.getenv("EMAIL_ADDRESS"),
        "gmail_app_password": os.getenv("GMAIL_APP_PASSWORD"),
        "max_rows": 100,
        "send_emails": send_emails
    }

    print("📊 Configuration:")
    print(f"   Spreadsheet: {workflow_input['spreadsheet_id']}")
    print(f"   Email mode: {'SEND' if send_emails else 'DRAFT'}")
    print(f"   Max rows: {workflow_input['max_rows']}\n")

    # Start the workflow - THIS IS ALL WE NEED!
    print("🚀 Starting Julep workflow...")
    print("   Julep will handle all orchestration internally\n")

    try:
        execution = client.executions.create(
            task_id=task_id,
            input=workflow_input
        )

        print(f"✅ Workflow started!")
        print(f"   Execution ID: {execution.id}")
        print(f"   Dashboard: https://dashboard.julep.ai/executions/{execution.id}\n")

        if mode == "fire_and_forget":
            print("🏃 Agent is running autonomously on Julep's infrastructure")
            print("   You can close this script - the agent continues running")
            print(f"   Check status later with: python start_agent_simple.py --status {execution.id}")
            return execution.id

        elif mode == "monitor":
            print("📡 Monitoring execution...\n")
            monitor_workflow(client, execution.id)

        return execution.id

    except Exception as e:
        print(f"❌ Failed to start workflow: {e}")
        return None


def monitor_workflow(client, execution_id):
    """Monitor the workflow execution with polling"""

    print("⏳ Checking status every 5 seconds (Ctrl+C to detach)...\n")

    try:
        max_wait = 600  # 10 minutes max
        check_interval = 5  # Check every 5 seconds

        for i in range(0, max_wait, check_interval):
            try:
                status = client.executions.get(execution_id)

                elapsed = f"{i}s" if i > 0 else "0s"
                print(f"\r   [{elapsed}] Status: {status.status}", end="", flush=True)

                if status.status == "succeeded":
                    print(" ✅")
                    print("\n" + "=" * 60)
                    print("🎉 WORKFLOW COMPLETED!")
                    print("=" * 60)

                    # Get final results
                    if hasattr(status, 'output') and status.output:
                        output = status.output
                        print("\n📊 Final Results:")
                        print(f"   Total rows checked: {output.get('total_rows_checked', 0)}")
                        print(f"   Pending rows found: {output.get('pending_rows_found', 0)}")
                        print(f"   Rows processed: {output.get('rows_processed', 0)}")
                        print(f"   Email mode: {output.get('email_mode', 'drafts')}")

                        if 'report' in output:
                            print("\n📝 Report:")
                            print(output['report'])
                    break

                elif status.status == "failed":
                    print(" ❌")
                    print("\n❌ WORKFLOW FAILED!")
                    if hasattr(status, 'error'):
                        print(f"   Error: {status.error}")
                    break

                elif status.status in ["cancelled", "stopped"]:
                    print(f" ⚠️ {status.status}")
                    break

                time.sleep(check_interval)

            except Exception as e:
                print(f"\n❌ Error checking status: {e}")
                break

    except KeyboardInterrupt:
        print("\n\n⚠️  Detached from monitoring (workflow continues running)")
        print(f"   Check status: python start_agent_simple.py --status {execution_id}")


def check_execution_status(execution_id):
    """Check the status of an existing execution"""

    client = Julep(api_key=os.getenv("JULEP_API_KEY"))

    print(f"🔍 Checking execution: {execution_id}\n")

    try:
        status = client.executions.get(execution_id)

        print(f"📊 Status: {status.status.upper()}")

        if status.status == "running":
            print("   Still processing...")

        elif status.status == "succeeded":
            if hasattr(status, 'output') and status.output:
                output = status.output
                print("\n✅ Completed Successfully!")
                print(f"   Rows processed: {output.get('rows_processed', 0)}")
                print(f"   Email mode: {output.get('email_mode', 'drafts')}")

        elif status.status == "failed":
            print("\n❌ Execution failed")
            if hasattr(status, 'error'):
                print(f"   Error: {status.error}")

    except Exception as e:
        print(f"❌ Error checking status: {e}")


def main():
    """Main entry point"""

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status" and len(sys.argv) > 2:
            # Check status of existing execution
            check_execution_status(sys.argv[2])
            return
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python start_agent_simple.py              # Start with monitoring")
            print("  python start_agent_simple.py --fire       # Start and exit")
            print("  python start_agent_simple.py --status ID  # Check execution status")
            return
        elif sys.argv[1] == "--fire":
            # Fire and forget mode
            start_youtube_agent(mode="fire_and_forget")
            return

    # Interactive mode
    print("🎯 YouTube Outreach Agent - Julep Native\n")
    print("Choose mode:")
    print("1. Monitor mode (see status updates)")
    print("2. Fire and forget (start and exit)")
    print("3. Check existing execution status")
    print("4. Exit")

    choice = input("\nSelect (1-4): ").strip()

    if choice == "1":
        # Monitor mode
        print("\n📧 Email configuration:")
        print("1. Save as DRAFTS (recommended)")
        print("2. SEND emails")

        email_choice = input("\nSelect (1-2): ").strip()
        send_emails = (email_choice == "2")

        if send_emails:
            confirm = input("\n⚠️  SEND emails? Type 'yes' to confirm: ").strip()
            if confirm.lower() != 'yes':
                send_emails = False

        start_youtube_agent(mode="monitor", send_emails=send_emails)

    elif choice == "2":
        # Fire and forget
        start_youtube_agent(mode="fire_and_forget", send_emails=False)

    elif choice == "3":
        # Check status
        execution_id = input("Enter Execution ID: ").strip()
        if execution_id:
            check_execution_status(execution_id)

    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()