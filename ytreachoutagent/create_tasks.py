#!/usr/bin/env python3
"""
Create Julep tasks from YAML definitions
This script only creates the tasks - all logic is in the YAML
"""

import os
import yaml
from dotenv import load_dotenv
from julep import Julep

load_dotenv()

def create_workflow_task():
    """Create the main workflow task from YAML definition"""

    print("=" * 60)
    print("CREATING JULEP WORKFLOW TASK")
    print("=" * 60)

    # Initialize Julep client
    client = Julep(api_key=os.getenv("JULEP_API_KEY"))
    agent_id = os.getenv("AGENT_ID")

    print(f"\n🤖 Agent ID: {agent_id}")

    # Load task definition from YAML
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
        print(f"   Task Name: {task.name}")

        # Save task ID to .env for future use
        save_task_id_to_env(task.id, 'WORKFLOW_TASK_ID')

        return task.id

    except Exception as e:
        print(f"❌ Failed to create task: {e}")
        return None


def save_task_id_to_env(task_id, env_key):
    """Save task ID to .env file"""

    env_path = '.env'

    # Read current .env content
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Check if key exists and update or append
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f'{env_key}='):
            lines[i] = f'{env_key}={task_id}\n'
            key_found = True
            break

    if not key_found:
        # Add new line if key doesn't exist
        lines.append(f'\n# Workflow Task\n{env_key}={task_id}\n')

    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ Saved {env_key} to .env")


def list_existing_tasks():
    """List all existing tasks for the agent"""

    client = Julep(api_key=os.getenv("JULEP_API_KEY"))
    agent_id = os.getenv("AGENT_ID")

    print("\n📋 Existing tasks for this agent:")
    try:
        tasks = client.tasks.list(agent_id=agent_id)
        if tasks.items:
            for task in tasks.items:
                print(f"   - {task.name} (ID: {task.id})")
        else:
            print("   No tasks found")
    except Exception as e:
        print(f"   Error listing tasks: {e}")


def main():
    """Main execution"""

    # Check for required environment variables
    required_vars = ['JULEP_API_KEY', 'AGENT_ID', 'APIFY_TOKEN', 'GOOGLE_SHEET_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return

    # List existing tasks
    list_existing_tasks()

    # Create the workflow task
    print("\n" + "=" * 60)
    task_id = create_workflow_task()

    if task_id:
        print("\n" + "=" * 60)
        print("✅ TASK CREATION COMPLETE!")
        print("\n📝 Next steps:")
        print("1. Run the workflow with: python run_workflow.py")
        print("2. Monitor execution in Julep dashboard")
        print("3. Check Google Sheets for status updates")
        print("=" * 60)
    else:
        print("\n❌ Task creation failed. Please check the errors above.")


if __name__ == "__main__":
    main()