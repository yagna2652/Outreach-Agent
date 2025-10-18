#!/usr/bin/env python3
"""
Check execution status and details
"""

import os
import sys
from dotenv import load_dotenv
from julep import Julep

# Load environment variables
load_dotenv()

def check_execution(execution_id=None):
    """Check execution status and details"""

    # Initialize Julep client
    client = Julep(api_key=os.getenv("JULEP_API_KEY"))

    if execution_id:
        # Check specific execution
        try:
            execution = client.executions.get(execution_id)
            print(f"Execution ID: {execution_id}")
            print(f"Status: {execution.status if hasattr(execution, 'status') else 'Unknown'}")

            if hasattr(execution, 'output'):
                print(f"Output: {execution.output}")

            if hasattr(execution, 'error'):
                print(f"Error: {execution.error}")

            # Try to get transitions (execution steps)
            try:
                transitions = client.executions.transitions.list(execution_id=execution_id)
                print("\nExecution Steps:")
                for i, transition in enumerate(transitions):
                    print(f"  Step {i}: {transition}")
            except:
                print("Could not fetch execution transitions")

        except Exception as e:
            print(f"Error fetching execution: {e}")
    else:
        # List recent executions
        print("Recent Executions:")
        print("-" * 60)

        # We need an agent ID to list executions
        agent_id = os.getenv("YOUTUBE_MONITOR_AGENT_ID")
        if not agent_id:
            print("No agent ID found in environment")
            return

        try:
            # Note: The API might not support listing all executions
            # This is a placeholder for the correct method
            print(f"Agent ID: {agent_id}")
            print("\nTo check specific execution, run:")
            print("  python check_execution.py <execution_id>")
            print("\nRecent execution IDs from test runs:")
            print("  068f382c-c199-78cb-8000-36dc0901d14c  (test_no_input)")
            print("  068f3828-2b6a-7c33-8000-1c9105e0acfb  (test_hardcoded)")
            print("  068f3827-2763-716f-8000-4966f41e4ce1  (test_hardcoded)")

        except Exception as e:
            print(f"Error listing executions: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_execution(sys.argv[1])
    else:
        check_execution()