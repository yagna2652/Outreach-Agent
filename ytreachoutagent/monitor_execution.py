#!/usr/bin/env python3
"""
Monitor a running Julep execution
Useful for checking on long-running workflows
"""

import os
import sys
import time
import json
from dotenv import load_dotenv
from julep import Julep

load_dotenv()


def monitor_execution(execution_id=None):
    """Monitor execution by ID"""

    print("=" * 60)
    print("JULEP EXECUTION MONITOR")
    print("=" * 60)

    client = Julep(api_key=os.getenv("JULEP_API_KEY"))

    # If no execution ID provided, prompt for one
    if not execution_id:
        execution_id = input("\n📝 Enter Execution ID to monitor: ").strip()

    if not execution_id:
        print("❌ No execution ID provided")
        return

    print(f"\n🔍 Monitoring execution: {execution_id}")

    # Get initial status
    try:
        status = client.executions.get(execution_id)
        print(f"✅ Found execution")
        print(f"   Current status: {status.status}")

        # If already completed, show results
        if status.status in ["succeeded", "failed", "cancelled"]:
            show_results(status)
            return

    except Exception as e:
        print(f"❌ Error getting execution: {e}")
        return

    # Monitor until completion
    print("\n⏳ Waiting for completion...")
    print("   Press Ctrl+C to stop monitoring\n")

    try:
        while True:
            status = client.executions.get(execution_id)
            print(f"\r   Status: {status.status}", end="", flush=True)

            if status.status == "succeeded":
                print(" ✅")
                show_results(status)
                break

            elif status.status in ["failed", "cancelled"]:
                print(f" {status.status.upper()}")
                show_results(status)
                break

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n⚠️ Monitoring stopped (execution still running)")
        print(f"   Resume monitoring with: python monitor_execution.py")
        print(f"   Execution ID: {execution_id}")


def show_results(status):
    """Display execution results"""

    print("\n" + "=" * 60)
    print("EXECUTION RESULTS")
    print("=" * 60)

    print(f"\nFinal Status: {status.status.upper()}")

    if hasattr(status, 'output'):
        print("\n📊 Output:")
        output = status.output

        if isinstance(output, dict):
            # Pretty print dictionary output
            for key, value in output.items():
                print(f"   {key}: {value}")
        else:
            # Print raw output
            output_str = str(output)
            if len(output_str) > 1000:
                print(output_str[:1000] + "...\n   [Output truncated]")
            else:
                print(output_str)

    if hasattr(status, 'error') and status.error:
        print(f"\n❌ Error: {status.error}")


def list_recent_executions():
    """List recent executions for the workflow task"""

    client = Julep(api_key=os.getenv("JULEP_API_KEY"))
    task_id = os.getenv("WORKFLOW_TASK_ID")

    if not task_id:
        print("\n⚠️ No WORKFLOW_TASK_ID found in .env")
        return

    print("\n📋 Recent executions for workflow task:")
    try:
        # Note: This might need adjustment based on actual Julep API
        # Showing conceptual code for listing executions
        print("   [Feature depends on Julep API support]")
        print(f"   Task ID: {task_id}")

    except Exception as e:
        print(f"   Error listing executions: {e}")


def main():
    """Main execution"""

    if len(sys.argv) > 1:
        # Execution ID provided as argument
        execution_id = sys.argv[1]
        monitor_execution(execution_id)
    else:
        # Interactive mode
        print("\n📋 Options:")
        print("1. Monitor specific execution by ID")
        print("2. List recent executions")
        print("3. Exit")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            monitor_execution()
        elif choice == "2":
            list_recent_executions()
        elif choice == "3":
            print("Goodbye!")
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()