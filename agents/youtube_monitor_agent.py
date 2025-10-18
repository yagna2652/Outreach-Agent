#!/usr/bin/env python3
"""
Intelligent YouTube Monitor Agent
This agent has memory, learns from interactions, and improves over time
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from julep import Julep


class YouTubeMonitorAgent:
    """Intelligent agent for YouTube outreach with persistent memory"""

    def __init__(self, api_key: str = None):
        """Initialize the intelligent agent"""
        self.client = Julep(api_key=api_key or os.getenv("JULEP_API_KEY"))
        self.agent = None
        self.session = None
        self.tasks = {}

        # Load saved task IDs from environment
        self._load_saved_tasks()

    def create_or_get_agent(self) -> str:
        """Create or retrieve the intelligent agent"""

        # Check if agent already exists in env
        agent_id = os.getenv("YOUTUBE_MONITOR_AGENT_ID")

        if agent_id:
            try:
                self.agent = self.client.agents.get(agent_id)
                print(f"✅ Retrieved existing agent: {self.agent.name}")
                return agent_id
            except:
                print("⚠️  Existing agent not found, creating new one...")

        # Create new intelligent agent
        self.agent = self.client.agents.create(
            name="YouTube Outreach Specialist",
            model="claude-3.5-sonnet",
            about="An intelligent agent that monitors YouTube channels, analyzes content, and performs personalized outreach",

            instructions=[
                # Core Mission
                "You are an expert at YouTube creator outreach and relationship building",

                # Memory and Learning
                "Remember all interactions with each creator",
                "Learn from successful email patterns and response rates",
                "Adapt your approach based on what works",
                "Track which creators respond positively",

                # Personalization
                "Always personalize outreach based on video content",
                "Reference specific moments from videos",
                "Understand each creator's style and audience",
                "Adjust tone to match the creator's communication style",

                # Continuous Improvement
                "Analyze patterns in successful outreach",
                "Identify optimal timing for different creator types",
                "Learn from failed attempts and adjust strategy",
                "Build a knowledge base of creator preferences",

                # Autonomy
                "Operate independently with minimal supervision",
                "Make intelligent decisions about prioritization",
                "Handle errors gracefully and retry with different approaches",
                "Alert only for critical issues or exceptional opportunities"
            ],

            metadata={
                "version": "2.0",
                "capabilities": [
                    "transcript_analysis",
                    "email_generation",
                    "pattern_recognition",
                    "autonomous_operation",
                    "continuous_learning"
                ],
                "created_at": datetime.now().isoformat()
            }
        )

        print(f"✅ Created intelligent agent: {self.agent.name}")
        print(f"   Agent ID: {self.agent.id}")

        # Save agent ID to env for future use
        self._save_to_env("YOUTUBE_MONITOR_AGENT_ID", self.agent.id)

        return self.agent.id

    def create_or_get_session(self) -> str:
        """Create or retrieve persistent session with memory"""

        # Check for existing session
        session_id = os.getenv("YOUTUBE_MONITOR_SESSION_ID")

        if session_id:
            try:
                self.session = self.client.sessions.get(session_id)
                print(f"✅ Retrieved existing session with memory")
                return session_id
            except:
                print("⚠️  Existing session not found, creating new one...")

        # Create new session with persistent context
        # Note: agent_id might need to be passed differently based on SDK version
        self.session = self.client.sessions.create(
            agent=self.agent.id,  # Try 'agent' instead of 'agent_id'

            # Persistent memory across runs
            metadata={
                "created_at": datetime.now().isoformat(),
                "last_check": None,
                "processed_videos": [],
                "total_processed": 0,
                "successful_patterns": [],
                "creator_profiles": {},
                "response_rates": {
                    "overall": 0,
                    "by_category": {}
                },
                "optimal_times": {
                    "best_day": None,
                    "best_hour": None
                },
                "campaign_stats": {
                    "emails_sent": 0,
                    "emails_opened": 0,
                    "responses_received": 0
                }
            }
        )

        print(f"✅ Created persistent session with memory")
        print(f"   Session ID: {self.session.id}")

        # Save session ID
        self._save_to_env("YOUTUBE_MONITOR_SESSION_ID", self.session.id)

        return self.session.id

    def upload_knowledge_documents(self):
        """Upload knowledge base documents for the agent"""

        print("\n📚 Uploading knowledge base...")

        # TODO: The document API has changed in newer Julep versions
        # For now, we'll skip document uploads and embed knowledge directly in agent instructions
        print("   ⚠️  Document API has changed - skipping document upload")
        print("   ℹ️  Knowledge is embedded in agent instructions instead")

        # In future versions, check Julep docs for the correct document API:
        # https://docs.julep.ai/

    def register_tasks(self, task_dir: str = "tasks"):
        """Register all tasks with the agent"""

        print("\n📋 Registering tasks...")

        # Task configurations - using MCP integration for APIFY
        task_configs = {
            "process_video": f"{task_dir}/workflows/process_single_video_fixed.yaml",
            "continuous_monitor": f"{task_dir}/autonomous/continuous_monitor_fixed.yaml"
        }

        for name, path in task_configs.items():
            try:
                # Load task definition
                import yaml
                with open(path, 'r') as f:
                    task_def = yaml.safe_load(f)

                # Create task
                task = self.client.tasks.create(
                    agent_id=self.agent.id,  # Back to agent_id
                    **task_def
                )

                self.tasks[name] = task.id
                print(f"   ✅ Registered: {name} ({task.id})")

            except Exception as e:
                print(f"   ❌ Failed to register {name}: {e}")

        # Save task IDs to env
        for name, task_id in self.tasks.items():
            self._save_to_env(f"TASK_{name.upper()}_ID", task_id)

        return self.tasks

    def deploy_autonomous_monitor(self, config: Dict):
        """Deploy the agent for autonomous monitoring"""

        print("\n🚀 Deploying autonomous monitor...")

        if "continuous_monitor" not in self.tasks:
            print("❌ Continuous monitor task not registered")
            return None

        # Start autonomous monitoring
        execution = self.client.executions.create(
            task_id=self.tasks["continuous_monitor"],
            input={
                "mode": config.get("mode", "continuous"),
                "check_interval_hours": config.get("interval_hours", 6),
                "spreadsheet_id": config["spreadsheet_id"],
                "google_auth_token": config["google_auth_token"],
                "apify_token": config["apify_token"],
                "max_videos_per_run": config.get("max_videos", 10),
                "send_emails": config.get("send_emails", False)
            }
        )

        print(f"✅ Autonomous agent deployed!")
        print(f"   Execution ID: {execution.id}")
        print(f"   Mode: {config.get('mode', 'continuous')}")
        print(f"   Interval: {config.get('interval_hours', 6)} hours")
        print(f"\n🤖 The agent is now running autonomously on Julep's infrastructure")
        print("   You can close this script - the agent continues working")
        print(f"   Monitor at: https://dashboard.julep.ai/executions/{execution.id}")

        return execution.id

    def get_agent_status(self) -> Dict:
        """Get current status and statistics from the agent"""

        if not self.session:
            return {"error": "No session found"}

        try:
            # Get session metadata
            session_data = self.client.sessions.get(self.session.id)
            metadata = session_data.metadata if hasattr(session_data, 'metadata') else {}

            return {
                "agent_id": self.agent.id,
                "session_id": self.session.id,
                "last_check": metadata.get("last_check", "Never"),
                "total_processed": metadata.get("total_processed", 0),
                "campaign_stats": metadata.get("campaign_stats", {}),
                "response_rates": metadata.get("response_rates", {}),
                "status": "Active"
            }
        except Exception as e:
            return {"error": str(e)}

    def _save_to_env(self, key: str, value: str):
        """Save a value to .env file"""
        env_path = '.env'

        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update or append
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                key_found = True
                break

        if not key_found:
            lines.append(f'{key}={value}\n')

        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)

    def _load_saved_tasks(self):
        """Load saved task IDs from environment"""
        # Load task IDs if they exist
        process_video_id = os.getenv("TASK_PROCESS_VIDEO_ID")
        continuous_monitor_id = os.getenv("TASK_CONTINUOUS_MONITOR_ID")

        if process_video_id:
            self.tasks["process_video"] = process_video_id
            print(f"   📂 Loaded saved task: process_video ({process_video_id})")

        if continuous_monitor_id:
            self.tasks["continuous_monitor"] = continuous_monitor_id
            print(f"   📂 Loaded saved task: continuous_monitor ({continuous_monitor_id})")


def setup_intelligent_agent():
    """Complete setup of the intelligent agent"""

    print("=" * 60)
    print("🤖 SETTING UP INTELLIGENT YOUTUBE MONITOR AGENT")
    print("=" * 60)

    agent = YouTubeMonitorAgent()

    # 1. Create or get agent
    agent.create_or_get_agent()

    # 2. Create or get session
    agent.create_or_get_session()

    # 3. Upload knowledge base
    agent.upload_knowledge_documents()

    # 4. Register tasks
    agent.register_tasks()

    # 5. Show status
    print("\n" + "=" * 60)
    print("✅ AGENT SETUP COMPLETE!")
    print("=" * 60)

    status = agent.get_agent_status()
    print("\n📊 Agent Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")

    print("\n📝 Next Steps:")
    print("1. Run 'python main.py deploy' to start autonomous monitoring")
    print("2. Run 'python main.py status' to check agent status")
    print("3. The agent will learn and improve over time")

    return agent


if __name__ == "__main__":
    setup_intelligent_agent()