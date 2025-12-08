# mcp_server/server.py
"""
MCP Server implementation for customer support system.
Exposes tools via the Model Context Protocol.
"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import get_tool_definitions, execute_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CustomerSupportMCPServer:
    """MCP Server for customer support operations."""
    
    def __init__(self):
        self.server = Server("customer-support-mcp")
        self.setup_handlers()
        logger.info("Customer Support MCP Server initialized")
    
    def setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""
            logger.info("Listing available tools")
            return get_tool_definitions()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a tool by name."""
            logger.info(f"Tool call received: {name}")
            return await execute_tool(name, arguments)
    
    async def run(self):
        """Run the MCP server using stdio transport."""
        logger.info("Starting MCP server with stdio transport")
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise


async def main():
    """Main entry point for the MCP server."""
    server = CustomerSupportMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())