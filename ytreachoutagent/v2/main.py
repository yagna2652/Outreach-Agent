#!/usr/bin/env python3
"""
Main Orchestrator for Julep-Native YouTube Outreach Agent
Single entry point for all operations
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.youtube_monitor_agent import YouTubeMonitorAgent


class JulepOrchestrator:
    """Main orchestrator for the YouTube outreach system"""

    def __init__(self):
        """Initialize the orchestrator"""
        self.agent = YouTubeMonitorAgent()
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from environment"""
        return {
            "spreadsheet_id": os.getenv("GOOGLE_SHEET_ID"),
            "apify_token": os.getenv("APIFY_TOKEN"),
            "email_address": os.getenv("EMAIL_ADDRESS"),
            "gmail_app_password": os.getenv("GMAIL_APP_PASSWORD"),
            "interval_hours": int(os.getenv("CHECK_INTERVAL_HOURS", "6")),
            "max_videos": int(os.getenv("MAX_VIDEOS_PER_RUN", "10"))
        }

    def _get_google_auth_token(self) -> str:
        """Get Google OAuth2 access token"""
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

    def setup(self):
        """Initial setup of agent and tasks"""
        print("\n🔧 INITIAL SETUP")
        print("=" * 60)

        # Create/get agent
        self.agent.create_or_get_agent()

        # Create/get session
        self.agent.create_or_get_session()

        # Upload knowledge
        self.agent.upload_knowledge_documents()

        # Register tasks
        self.agent.register_tasks()

        print("\n✅ Setup complete! Agent is ready for deployment.")

    def deploy(self, mode: str = "continuous", send_emails: bool = False):
        """Deploy the autonomous agent"""

        print("\n🚀 DEPLOYING AUTONOMOUS AGENT")
        print("=" * 60)

        # Get Google auth
        google_token = self._get_google_auth_token()
        if not google_token:
            print("❌ Cannot deploy without Google authentication")
            return

        # Prepare deployment config
        deploy_config = {
            **self.config,
            "google_auth_token": google_token,
            "mode": mode,
            "send_emails": send_emails
        }

        print(f"\n📋 Deployment Configuration:")
        print(f"   Mode: {mode}")
        print(f"   Check interval: {self.config['interval_hours']} hours")
        print(f"   Max videos/run: {self.config['max_videos']}")
        print(f"   Email mode: {'SEND' if send_emails else 'DRAFT'}")
        print(f"   Spreadsheet: {self.config['spreadsheet_id']}")

        if send_emails and mode == "continuous":
            confirm = input("\n⚠️  WARNING: Emails will be SENT automatically! Continue? (yes/no): ")
            if confirm.lower() != "yes":
                print("❌ Deployment cancelled")
                return

        # Ensure agent exists
        if not self.agent.agent:
            self.agent.create_or_get_agent()
        if not self.agent.session:
            self.agent.create_or_get_session()

        # Deploy
        execution_id = self.agent.deploy_autonomous_monitor(deploy_config)

        if execution_id and mode == "continuous":
            print("\n📝 Important Notes:")
            print("   • The agent is now running on Julep's infrastructure")
            print("   • You can safely close this terminal")
            print("   • The agent will continue processing every", self.config['interval_hours'], "hours")
            print("   • To stop: python main.py stop", execution_id)

        return execution_id

    def status(self, execution_id: str = None):
        """Check agent and execution status"""

        print("\n📊 AGENT STATUS")
        print("=" * 60)

        # Get agent status
        status = self.agent.get_agent_status()

        print("\n🤖 Agent Information:")
        for key, value in status.items():
            if key != "campaign_stats":
                print(f"   {key}: {value}")

        if "campaign_stats" in status and status["campaign_stats"]:
            print("\n📈 Campaign Statistics:")
            for key, value in status["campaign_stats"].items():
                print(f"   {key}: {value}")

        # Check specific execution if provided
        if execution_id:
            print(f"\n🔍 Checking execution: {execution_id}")
            try:
                from julep import Julep
                client = Julep(api_key=os.getenv("JULEP_API_KEY"))
                exec_status = client.executions.get(execution_id)
                print(f"   Status: {exec_status.status}")

                if hasattr(exec_status, 'output') and exec_status.output:
                    # Check if output is a dict before calling .get()
                    if isinstance(exec_status.output, dict):
                        print(f"   Videos processed: {exec_status.output.get('videos_processed', 'N/A')}")
                        print(f"   Last check: {exec_status.output.get('last_check', 'N/A')}")
                    else:
                        print(f"   Output: {exec_status.output}")

            except Exception as e:
                print(f"   Error: {e}")

    def run_once(self, send_emails: bool = False):
        """Run the monitor once (not continuous)"""
        print("\n▶️  RUNNING SINGLE CYCLE")
        return self.deploy(mode="once", send_emails=send_emails)

    def test(self):
        """Test mode - process one video as draft"""
        print("\n🧪 TEST MODE")
        print("=" * 60)
        print("This will process videos once and save as drafts")
        return self.run_once(send_emails=False)

    def help(self):
        """Show help information"""
        help_text = """
YouTube Outreach Agent - Julep Native
=====================================

Commands:
  python main.py setup       - Initial setup of agent and tasks
  python main.py deploy      - Deploy autonomous monitoring agent
  python main.py test        - Test mode (process once, drafts only)
  python main.py run-once    - Run one cycle and exit
  python main.py status      - Check agent status and stats
  python main.py status ID   - Check specific execution status
  python main.py help        - Show this help message

Deployment Options:
  --continuous    Deploy in continuous mode (default)
  --once         Run once and exit
  --send         Actually send emails (default: drafts only)

Examples:
  python main.py setup                    # First time setup
  python main.py deploy                   # Start continuous monitoring
  python main.py deploy --once --send     # Run once and send emails
  python main.py status abc123            # Check execution abc123

Environment Variables:
  JULEP_API_KEY            Julep API key (required)
  GOOGLE_SHEET_ID          Google Sheets ID (required)
  APIFY_TOKEN             APIFY API token (required)
  EMAIL_ADDRESS           Sender email address
  GMAIL_APP_PASSWORD      Gmail app password
  CHECK_INTERVAL_HOURS    Hours between checks (default: 6)
  MAX_VIDEOS_PER_RUN     Max videos to process per run (default: 10)
        """
        print(help_text)


def main():
    """Main entry point"""

    orchestrator = JulepOrchestrator()

    # Parse command line arguments
    args = sys.argv[1:]

    if not args:
        orchestrator.help()
        return

    command = args[0].lower()

    # Command routing
    if command == "setup":
        orchestrator.setup()

    elif command == "deploy":
        mode = "continuous"
        send_emails = False

        if "--once" in args:
            mode = "once"
        if "--send" in args:
            send_emails = True

        orchestrator.deploy(mode=mode, send_emails=send_emails)

    elif command == "test":
        orchestrator.test()

    elif command == "run-once":
        send_emails = "--send" in args
        orchestrator.run_once(send_emails=send_emails)

    elif command == "status":
        execution_id = args[1] if len(args) > 1 else None
        orchestrator.status(execution_id)

    elif command == "help":
        orchestrator.help()

    else:
        print(f"❌ Unknown command: {command}")
        orchestrator.help()


if __name__ == "__main__":
    # Check for required environment variables
    required = ["JULEP_API_KEY", "GOOGLE_SHEET_ID", "APIFY_TOKEN"]
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("   Please check your .env file")
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)