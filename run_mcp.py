# run_mcp.py
"""
Working MCP implementation using async/await properly.
This uses the REAL MCP protocol with stdio transport.
"""

import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.config import Config
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPAgentSession:
    """Agent session using real MCP protocol."""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or Config.DEFAULT_USER_ID
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.conversation_history = []
        self.mcp_session = None
        self.stdio_context = None
        self.available_tools = []
        logger.info(f"Agent session created for user: {self.user_id}")
    
    async def connect_mcp(self):
        """Connect to MCP server."""
        server_script = Path(__file__).parent / "mcp_server" / "server.py"
        
        logger.info(f"Connecting to MCP server: {server_script}")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[str(server_script)],
            env=None
        )
        
        # Connect using stdio - use context manager properly
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()
        
        # Create MCP session
        self.mcp_session = ClientSession(self.read_stream, self.write_stream)
        
        # Initialize the session
        await self.mcp_session.__aenter__()
        await self.mcp_session.initialize()
        
        # List available tools
        tools_result = await self.mcp_session.list_tools()
        self.available_tools = self._convert_tools(tools_result.tools)
        
        logger.info(f"✓ MCP connected! Loaded {len(self.available_tools)} tools")
    
    def _convert_tools(self, mcp_tools):
        """Convert MCP tools to Anthropic format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in mcp_tools
        ]
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """Call a tool via MCP protocol."""
        # Inject user_id
        arguments["user_id"] = self.user_id
        
        logger.info(f"Calling MCP tool: {tool_name}")
        
        # Call tool through MCP
        result = await self.mcp_session.call_tool(tool_name, arguments)
        
        # Extract text from result
        if result.content and len(result.content) > 0:
            return result.content[0].text
        return "{}"
    
    async def chat(self, user_message: str) -> str:
        """Process a message with tool calling."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        logger.info(f"Processing: {user_message[:50]}...")
        
        # Call Claude with tools
        response = self.client.messages.create(
            model=Config.MODEL_NAME,
            max_tokens=Config.MAX_TOKENS,
            system=Config.get_system_prompt(),
            messages=self.conversation_history,
            tools=self.available_tools
        )
        
        # Handle tool use loop
        while any(block.type == "tool_use" for block in response.content):
            logger.info("Tool use detected, executing...")
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await self.call_mcp_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add tool results to history
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue conversation
            response = self.client.messages.create(
                model=Config.MODEL_NAME,
                max_tokens=Config.MAX_TOKENS,
                system=Config.get_system_prompt(),
                messages=self.conversation_history,
                tools=self.available_tools
            )
        
        # Extract final text response
        final_response = ""
        for block in response.content:
            if block.type == "text":
                final_response += block.text
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response
    
    def reset(self):
        """Reset conversation."""
        self.conversation_history = []
        logger.info("Conversation reset")
    
    async def disconnect(self):
        """Disconnect from MCP."""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)
        if self.stdio_context:
            await self.stdio_context.__aexit__(None, None, None)
        logger.info("MCP disconnected")


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  Customer Support Assistant - Claude + MCP")
    print("  (Using REAL MCP Protocol with stdio transport)")
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


async def run_interactive():
    """Run interactive session."""
    print_banner()
    
    # Create and connect session
    session = MCPAgentSession(user_id=Config.DEFAULT_USER_ID)
    
    try:
        await session.connect_mcp()
        print(f"✓ Logged in as: {session.user_id}")
        print("  (Using MCP protocol for all tool calls)\n")
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
                    session.user_id = new_user_id
                    print(f"\n✓ Switched to: {new_user_id}\n")
                    continue
                
                print("\nAssistant: ", end="", flush=True)
                response = await session.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\nError: {e}\n")
    
    finally:
        await session.disconnect()


async def run_examples():
    """Run example queries."""
    print("Running MCP examples...\n")
    
    session = MCPAgentSession(user_id="user_001")
    
    try:
        await session.connect_mcp()
        
        examples = [
            "What's my account balance?",
            "Show my recent transactions",
            "Get my account details"
        ]
        
        for i, query in enumerate(examples, 1):
            print(f"\n{'='*60}")
            print(f"Example {i}: {query}")
            print('='*60)
            
            response = await session.chat(query)
            print(f"\n{response}\n")
    
    finally:
        await session.disconnect()


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        asyncio.run(run_examples())
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()