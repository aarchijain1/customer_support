# run_system.py
"""
Main entry point for the customer support system.
Demonstrates the full integration between Claude agent and MCP server.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.mcp_client import SyncMCPClient
from agent.claude_agent import AgentSession
from agent.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  Customer Support Assistant - Powered by Claude & MCP")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  - Type your request naturally")
    print("  - 'reset' - Clear conversation history")
    print("  - 'user <user_id>' - Switch user (e.g., 'user user_002')")
    print("  - 'exit' or 'quit' - Exit the application")
    print("\nExample requests:")
    print("  - What's my account balance?")
    print("  - Change my password to newSecurePass123")
    print("  - Show me my recent transactions")
    print("  - Deactivate my card")
    print("  - Update my address to 789 New St, Boston, MA")
    print("=" * 60)
    print()


def run_interactive_session():
    """Run an interactive CLI session."""
    print_banner()
    
    # Get MCP server path
    mcp_server_path = Path(__file__).parent / "mcp_server" / "server.py"
    
    if not mcp_server_path.exists():
        logger.error(f"MCP server not found at: {mcp_server_path}")
        print(f"\nError: MCP server not found at {mcp_server_path}")
        return
    
    print(f"Connecting to MCP server at: {mcp_server_path}")
    print("Please wait...\n")
    
    try:
        # Connect to MCP server and create agent session
        with SyncMCPClient(str(mcp_server_path)) as mcp_client:
            session = AgentSession(mcp_client, user_id=Config.DEFAULT_USER_ID)
            
            print(f"✓ Connected! Current user: {session.agent.user_id}\n")
            print("How can I help you today?\n")
            
            # Main conversation loop
            while True:
                try:
                    # Get user input
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['exit', 'quit']:
                        print("\nThank you for using our customer support system. Goodbye!")
                        break
                    
                    elif user_input.lower() == 'reset':
                        session.reset()
                        print("\n✓ Conversation reset\n")
                        continue
                    
                    elif user_input.lower().startswith('user '):
                        new_user_id = user_input.split(' ', 1)[1].strip()
                        session.set_user_id(new_user_id)
                        print(f"\n✓ Switched to user: {new_user_id}\n")
                        continue
                    
                    # Process message with agent
                    print("\nAssistant: ", end="", flush=True)
                    response = session.chat(user_input)
                    print(response)
                    print()
                    
                except KeyboardInterrupt:
                    print("\n\nExiting...")
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    print(f"\nError: {str(e)}\n")
                    print("Please try again or type 'exit' to quit.\n")
    
    except Exception as e:
        logger.error(f"Failed to start session: {str(e)}")
        print(f"\nFailed to connect to MCP server: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that your .env file has ANTHROPIC_API_KEY set")
        print("3. Verify the MCP server files exist in mcp_server/")


def run_example_queries():
    """Run a set of example queries to demonstrate the system."""
    print("Running example queries...\n")
    
    mcp_server_path = Path(__file__).parent / "mcp_server" / "server.py"
    
    example_queries = [
        "What's my account balance?",
        "Show me my recent transactions",
        "Change my password to newSecurePassword123",
        "Update my address to 456 Oak Street, Portland, OR 97201",
        "Get my full account details"
    ]
    
    try:
        with SyncMCPClient(str(mcp_server_path)) as mcp_client:
            session = AgentSession(mcp_client, user_id="user_001")
            
            for i, query in enumerate(example_queries, 1):
                print(f"\n{'='*60}")
                print(f"Example {i}: {query}")
                print('='*60)
                
                response = session.chat(query)
                print(f"\nResponse:\n{response}\n")
    
    except Exception as e:
        logger.error(f"Failed to run examples: {str(e)}")
        print(f"\nError running examples: {str(e)}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        run_example_queries()
    else:
        run_interactive_session()


if __name__ == "__main__":
    main()