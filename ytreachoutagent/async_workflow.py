#!/usr/bin/env python3
"""
Async version of run_workflow.py using Julep's AsyncClient
This provides parallel processing and real-time streaming updates
"""

import os
import asyncio
import yaml
from dotenv import load_dotenv
from julep import AsyncClient
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


async def create_or_get_task(client, agent_id):
    """Create the complete workflow task or get existing one"""

    # Check if we already have a task ID
    task_id = os.getenv("COMPLETE_WORKFLOW_TASK_ID")
    if not task_id:
        task_id = os.getenv("TASK_ID")

    if task_id:
        try:
            # Verify task exists
            task = await client.tasks.get(task_id)
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
        task = await client.tasks.create(
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


async def execute_workflow_async(send_emails=False):
    """Execute the YouTube outreach workflow asynchronously"""

    print("=" * 60)
    print("EXECUTING YOUTUBE OUTREACH WORKFLOW (ASYNC)")
    print("=" * 60)

    # Initialize Async Julep client
    client = AsyncClient(api_key=os.getenv("JULEP_API_KEY"))
    agent_id = os.getenv("AGENT_ID")

    # Get or create task
    task_id = await create_or_get_task(client, agent_id)
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
        "send_emails": send_emails
    }

    print(f"\n📊 Configuration:")
    print(f"   Spreadsheet ID: {execution_input['spreadsheet_id']}")
    print(f"   Email Address: {execution_input['email_address']}")
    print(f"   Email Mode: {'SEND EMAILS' if send_emails else 'SAVE AS DRAFTS'}")
    print(f"   Max rows to process: {execution_input['max_rows']}")

    # Start execution
    print("\n🚀 Starting workflow execution (async)...")
    try:
        execution = await client.executions.create(
            task_id=task_id,
            input=execution_input
        )
        print(f"✅ Execution started!")
        print(f"   Execution ID: {execution.id}")

        return execution.id

    except Exception as e:
        print(f"❌ Failed to start execution: {e}")
        return None


async def monitor_execution_with_streaming(execution_id):
    """Monitor execution with real-time streaming updates"""

    client = AsyncClient(api_key=os.getenv("JULEP_API_KEY"))

    print("\n📡 Monitoring execution with live streaming...")
    print("   Real-time updates will appear below:\n")

    try:
        # Stream execution status updates
        async for event in client.executions.status.stream(execution_id):
            # Handle different event types
            if event.type == "step:started":
                print(f"   ▶️  Step started: {event.name}")

            elif event.type == "step:completed":
                print(f"   ✅ Step completed: {event.name}")

            elif event.type == "tool:called":
                print(f"   🔧 Tool called: {event.tool_name}")

            elif event.type == "log":
                print(f"   📝 Log: {event.message}")

            elif event.type == "execution:completed":
                print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")

                # Get final execution status
                status = await client.executions.get(execution_id)

                if hasattr(status, 'output'):
                    output = status.output
                    print("\n📊 Results:")
                    if isinstance(output, dict):
                        print(f"   Total rows checked: {output.get('total_rows_checked', 'N/A')}")
                        print(f"   Pending rows found: {output.get('pending_rows_found', 'N/A')}")
                        print(f"   Rows processed: {output.get('rows_processed', 'N/A')}")
                        print(f"   Email mode: {output.get('email_mode', 'N/A')}")

                        if 'report' in output:
                            print("\n📝 Detailed Report:")
                            print(output['report'])

                return True

            elif event.type == "execution:failed":
                print("\n❌ WORKFLOW FAILED!")
                if hasattr(event, 'error'):
                    print(f"Error: {event.error}")
                return False

    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")
        return False


async def process_multiple_videos_parallel():
    """Example of processing multiple videos in parallel"""

    client = AsyncClient(api_key=os.getenv("JULEP_API_KEY"))
    task_id = os.getenv("TASK_ID")

    print("\n🚀 Processing multiple videos in parallel...")

    # Example video URLs to process
    video_urls = [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        "https://youtube.com/watch?v=ghi789"
    ]

    # Create execution tasks for all videos at once
    execution_tasks = []
    for url in video_urls:
        task = client.executions.create(
            task_id=task_id,
            input={"youtube_url": url}
        )
        execution_tasks.append(task)

    # Execute all in parallel
    print(f"   Processing {len(video_urls)} videos simultaneously...")
    results = await asyncio.gather(*execution_tasks)

    print(f"✅ All {len(results)} videos processed in parallel!")
    return results


async def main():
    """Main async execution"""

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

    print("\n🔄 ASYNC WORKFLOW RUNNER")
    print("=" * 60)
    print("Choose operation mode:")
    print("1. Run full workflow (async with streaming)")
    print("2. Process multiple videos in parallel (demo)")
    print("3. Monitor existing execution")

    choice = input("\nSelect mode (1-3): ").strip()

    if choice == "1":
        # Full workflow with streaming
        print("\n📧 Email Mode Selection:")
        print("1. Save as DRAFTS (recommended for testing)")
        print("2. SEND emails to recipients")

        email_choice = input("\nSelect mode (1 or 2): ").strip()
        send_emails = (email_choice == "2")

        if send_emails:
            print("\n⚠️  WARNING: Emails will be SENT to recipients!")
            confirm = input("   Type 'yes' to confirm sending emails: ").strip().lower()
            if confirm != 'yes':
                print("❌ Cancelled - switching to draft mode")
                send_emails = False

        # Execute the workflow
        execution_id = await execute_workflow_async(send_emails=send_emails)

        if execution_id:
            # Monitor with streaming
            success = await monitor_execution_with_streaming(execution_id)

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

            print(f"\n📊 View execution details at:")
            print(f"   https://dashboard.julep.ai/executions/{execution_id}")

    elif choice == "2":
        # Parallel processing demo
        results = await process_multiple_videos_parallel()
        print("\nResults from parallel processing:")
        for i, result in enumerate(results, 1):
            print(f"   Video {i}: {result.id}")

    elif choice == "3":
        # Monitor existing execution
        execution_id = input("\nEnter Execution ID to monitor: ").strip()
        if execution_id:
            await monitor_execution_with_streaming(execution_id)

    else:
        print("❌ Invalid option")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())