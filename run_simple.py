# run_simple.py
"""
Simplified runner that directly executes tools without MCP transport.
Use this as your main entry point.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.claude_agent import CustomerSupportAgent
from agent.config import Config
from mcp_server.tools import execute_tool
import asyncio

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DirectToolExecutor:
    """Executes tools directly without MCP transport."""
    
    def __init__(self):
        from mcp_server.tools import get_tool_definitions
        self.tools = get_tool_definitions()
    
    def list_tools(self):
        """List available tools."""
        return self.tools
    
    def call_tool(self, tool_name: str, arguments: dict):
        """Execute a tool directly."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(execute_tool(tool_name, arguments))
            # Extract text from TextContent
            if isinstance(result, list) and len(result) > 0:
                return result[0].text
            return str(result)
        finally:
            loop.close()


class SimpleAgentSession:
    """Simplified agent session using direct tool execution."""
    
    def __init__(self, user_id: str):
        self.agent = CustomerSupportAgent(user_id)
        self.tool_executor = DirectToolExecutor()
        
        # Load tools
        tools = self.tool_executor.list_tools()
        anthropic_tools = [self._convert_tool_format(tool) for tool in tools]
        self.agent.set_mcp_tools(anthropic_tools)
        
        logger.info(f"Session initialized for user: {user_id}")
    
    def _convert_tool_format(self, mcp_tool):
        """Convert MCP tool format to Anthropic format."""
        return {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "input_schema": mcp_tool.inputSchema
        }
    
    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool with automatic user_id injection."""
        # ALWAYS inject user_id from session - user is already authenticated
        arguments["user_id"] = self.agent.user_id
        
        logger.info(f"Executing {tool_name} for user {self.agent.user_id}")
        
        try:
            return self.tool_executor.call_tool(tool_name, arguments)
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            import json
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {tool_name}"
            })
    
    def chat(self, user_message: str) -> str:
        """Process a user message."""
        return self.agent.process_message(user_message, self._execute_tool)
    
    def reset(self):
        """Reset the conversation."""
        self.agent.reset_conversation()
    
    def set_user_id(self, user_id: str):
        """Update the user ID."""
        self.agent.set_user_id(user_id)


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  Customer Support Assistant - Powered by Claude")
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
    
    try:
        session = SimpleAgentSession(user_id=Config.DEFAULT_USER_ID)
        print(f"✓ Ready! Logged in as user: {session.agent.user_id}")
        print(f"  (You don't need to provide user_id - you're already authenticated!)\n")
        print("How can I help you today?\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
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
        print(f"\nFailed to initialize: {str(e)}")
        print("\nPlease check:")
        print("1. Your .env file has ANTHROPIC_API_KEY set")
        print("2. All dependencies are installed: pip install -r requirements.txt")


def run_example_queries():
    """Run example queries."""
    print("Running example queries...\n")
    
    example_queries = [
        "What's my account balance?",
        "Show me my recent transactions",
        "Get my full account details"
    ]
    
    try:
        session = SimpleAgentSession(user_id="user_001")
        
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