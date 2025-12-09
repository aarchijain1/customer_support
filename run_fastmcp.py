# run_fastmcp.py
"""
Customer Support Agent using FastMCP server.
This should work reliably on Windows.
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


class FastMCPAgent:
    """Agent using FastMCP server."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.conversation_history = []
        self.available_tools = []
        
        # MCP connection
        self.session = None
        self.stdio_ctx = None
        
        logger.info(f"Agent initialized for user: {user_id}")
    
    async def connect(self):
        """Connect to FastMCP server."""
        server_script = Path(__file__).parent / "mcp_server_fastmcp.py"
        
        logger.info(f"Connecting to FastMCP server: {server_script}")
        
        # Server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[str(server_script)],
            env=None
        )
        
        # Connect using stdio
        self.stdio_ctx = stdio_client(server_params)
        read, write = await self.stdio_ctx.__aenter__()
        
        # Create session
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        
        # Initialize
        await self.session.initialize()
        
        # Get tools
        tools_result = await self.session.list_tools()
        
        # Convert to Anthropic format
        self.available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools_result.tools
        ]
        
        logger.info(f"✓ Connected! Loaded {len(self.available_tools)} tools")
    
    async def disconnect(self):
        """Disconnect from server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.stdio_ctx:
            await self.stdio_ctx.__aexit__(None, None, None)
        logger.info("Disconnected from FastMCP server")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call a tool through FastMCP."""
        # Inject user_id
        arguments["user_id"] = self.user_id
        
        logger.info(f"[FastMCP] Calling tool: {tool_name}")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            if result.content and len(result.content) > 0:
                return result.content[0].text
            return "{}"
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            import json
            return json.dumps({"success": False, "error": str(e)})
    
    async def chat(self, user_message: str) -> str:
        """Process a user message."""
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        logger.info(f"Processing: {user_message[:50]}...")
        
        # Call Claude
        response = self.anthropic_client.messages.create(
            model=Config.MODEL_NAME,
            max_tokens=Config.MAX_TOKENS,
            system=Config.get_system_prompt(),
            messages=self.conversation_history,
            tools=self.available_tools
        )
        
        # Handle tool use loop
        while any(block.type == "tool_use" for block in response.content):
            logger.info("Tool use detected")
            
            # Add assistant response
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await self.call_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add tool results
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue
            response = self.anthropic_client.messages.create(
                model=Config.MODEL_NAME,
                max_tokens=Config.MAX_TOKENS,
                system=Config.get_system_prompt(),
                messages=self.conversation_history,
                tools=self.available_tools
            )
        
        # Extract text
        final_text = ""
        for block in response.content:
            if block.type == "text":
                final_text += block.text
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_text
        })
        
        return final_text
    
    def reset(self):
        """Reset conversation."""
        self.conversation_history = []


async def main():
    """Main interactive loop."""
    print("=" * 60)
    print("  Customer Support Assistant")
    print("  Using FastMCP Server (stdio)")
    print("=" * 60)
    print()
    
    agent = FastMCPAgent(user_id=Config.DEFAULT_USER_ID)
    
    try:
        # Connect
        print("Connecting to FastMCP server...")
        await agent.connect()
        print(f"✓ Connected! Logged in as: {agent.user_id}\n")
        print("How can I help you today?\n")
        
        # Interactive loop
        while True:
            try:
                loop = asyncio.get_event_loop()
                user_input = await loop.run_in_executor(
                    None,
                    lambda: input("You: ").strip()
                )
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\nGoodbye!")
                    break
                
                elif user_input.lower() == 'reset':
                    agent.reset()
                    print("\n✓ Conversation reset\n")
                    continue
                
                elif user_input.lower().startswith('user '):
                    new_user_id = user_input.split(' ', 1)[1].strip()
                    agent.user_id = new_user_id
                    print(f"\n✓ Switched to: {new_user_id}\n")
                    continue
                
                # Process
                print("\nAssistant: ", end="", flush=True)
                response = await agent.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\nError: {e}\n")
    
    finally:
        await agent.disconnect()


if __name__ == "__main__":
    asyncio.run(main())