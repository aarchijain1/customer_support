# run_mcp_http.py
"""
Customer Support Agent using MCP Server over HTTP.
This is the REAL MCP implementation that works on Windows.
"""

import sys
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from agent.claude_agent import CustomerSupportAgent
from agent.config import Config

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTTPMCPClient:
    """MCP Client that communicates over HTTP."""
    
    def __init__(self, server_url: str = "http://localhost:8765"):
        self.server_url = server_url
        self.tools_cache = None
        logger.info(f"MCP HTTP Client initialized: {server_url}")
    
    def check_connection(self) -> bool:
        """Check if MCP server is running."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server."""
        if self.tools_cache:
            return self.tools_cache
        
        try:
            response = requests.get(f"{self.server_url}/tools")
            response.raise_for_status()
            self.tools_cache = response.json()["tools"]
            logger.info(f"Loaded {len(self.tools_cache)} tools from MCP server")
            return self.tools_cache
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool via MCP server."""
        try:
            response = requests.post(
                f"{self.server_url}/tools/execute",
                json={"name": tool_name, "arguments": arguments},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["result"]
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            import json
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {tool_name}"
            })


class MCPAgentSession:
    """Agent session using HTTP MCP server."""
    
    def __init__(self, mcp_client: HTTPMCPClient, user_id: str):
        self.agent = CustomerSupportAgent(user_id)
        self.mcp_client = mcp_client
        
        # Load tools from MCP server
        tools = self.mcp_client.list_tools()
        self.agent.set_mcp_tools(tools)
        
        logger.info(f"Session initialized for user: {user_id}")
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool via MCP with automatic user_id injection."""
        # Inject user_id from session
        arguments["user_id"] = self.agent.user_id
        
        logger.info(f"[MCP] Calling tool: {tool_name} for user {self.agent.user_id}")
        
        # Call through MCP server
        return self.mcp_client.call_tool(tool_name, arguments)
    
    def chat(self, user_message: str) -> str:
        """Process a user message."""
        return self.agent.process_message(user_message, self._execute_tool)
    
    def reset(self):
        """Reset conversation."""
        self.agent.reset_conversation()
    
    def set_user_id(self, user_id: str):
        """Update user ID."""
        self.agent.set_user_id(user_id)


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  Customer Support Assistant")
    print("  Using MCP Server over HTTP")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  - Type your request naturally")
    print("  - 'reset' - Clear conversation history")
    print("  - 'user <user_id>' - Switch user")
    print("  - 'exit' or 'quit' - Exit")
    print("\nExample requests:")
    print("  - What's my account balance?")
    print("  - Show me my recent transactions")
    print("  - Change my password to NewPass123")
    print("=" * 60)
    print()


def run_interactive_session():
    """Run interactive CLI session."""
    print_banner()
    
    # Connect to MCP server
    mcp_client = HTTPMCPClient()
    
    # Check if server is running
    print("Connecting to MCP server...")
    if not mcp_client.check_connection():
        print("\n❌ ERROR: MCP server is not running!")
        print("\nPlease start the MCP server first:")
        print("  python mcp_http_server.py")
        print("\nThen run this script again.")
        return
    
    print("✓ Connected to MCP server\n")
    
    try:
        session = MCPAgentSession(mcp_client, user_id=Config.DEFAULT_USER_ID)
        print(f"✓ Logged in as: {session.agent.user_id}")
        print("  (All tool calls go through MCP server)\n")
        print("How can I help you today?\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\nGoodbye!")
                    break
                
                elif user_input.lower() == 'reset':
                    session.reset()
                    print("\n✓ Conversation reset\n")
                    continue
                
                elif user_input.lower().startswith('user '):
                    new_user_id = user_input.split(' ', 1)[1].strip()
                    session.set_user_id(new_user_id)
                    print(f"\n✓ Switched to: {new_user_id}\n")
                    continue
                
                print("\nAssistant: ", end="", flush=True)
                response = session.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\nError: {e}\n")
    
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        print(f"\nError: {e}")


def run_examples():
    """Run example queries."""
    print("Running MCP examples...\n")
    
    mcp_client = HTTPMCPClient()
    
    if not mcp_client.check_connection():
        print("❌ MCP server not running. Start it with: python mcp_http_server.py")
        return
    
    try:
        session = MCPAgentSession(mcp_client, user_id="user_001")
        
        examples = [
            "What's my account balance?",
            "Show my recent transactions",
            "Get my account details"
        ]
        
        for i, query in enumerate(examples, 1):
            print(f"\n{'='*60}")
            print(f"Example {i}: {query}")
            print('='*60)
            
            response = session.chat(query)
            print(f"\n{response}\n")
    
    except Exception as e:
        logger.error(f"Failed to run examples: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        run_examples()
    else:
        run_interactive_session()


if __name__ == "__main__":
    main()