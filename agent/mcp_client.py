# agent/mcp_client.py
"""
MCP Client for connecting the Claude agent to the MCP server.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for communicating with MCP server.
    """
    
    def __init__(self, server_script_path: str):
        """
        Initialize MCP client.
        
        Args:
            server_script_path: Path to the MCP server script
        """
        self.server_script_path = server_script_path
        self.session: ClientSession = None
        self.stdio_context = None
        self.read_stream = None
        self.write_stream = None
        logger.info(f"MCP Client initialized with server: {server_script_path}")
    
    async def connect(self):
        """Connect to the MCP server."""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path],
                env=None
            )
            
            # Get the stdio context manager
            self.stdio_context = stdio_client(server_params)
            
            # Enter the context manager
            self.read_stream, self.write_stream = await self.stdio_context.__aenter__()
            
            # Create and initialize session
            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()
            
            # Initialize the session
            await self.session.initialize()
            
            logger.info("Successfully connected to MCP server")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
            logger.info("Disconnected from MCP server")
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
    
    async def list_tools_async(self) -> List[Any]:
        """
        List available tools from the MCP server (async).
        
        Returns:
            List of tool definitions
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.list_tools()
            return result.tools
        except Exception as e:
            logger.error(f"Failed to list tools: {str(e)}")
            raise
    
    async def call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> List[Any]:
        """
        Call a tool on the MCP server (async).
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result.content
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {str(e)}")
            raise


class SyncMCPClient:
    """
    Synchronous wrapper for MCPClient.
    Manages the event loop internally for easier integration.
    """
    
    def __init__(self, server_script_path: str):
        """
        Initialize sync MCP client.
        
        Args:
            server_script_path: Path to the MCP server script
        """
        self.server_script_path = server_script_path
        self.client = None
        self.loop = None
        self._connected = False
    
    def _ensure_loop(self):
        """Ensure we have an event loop."""
        if self.loop is None or self.loop.is_closed():
            try:
                self.loop = asyncio.get_event_loop()
                if self.loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
    
    def connect(self):
        """Connect to the MCP server."""
        self._ensure_loop()
        self.client = MCPClient(self.server_script_path)
        self.loop.run_until_complete(self.client.connect())
        self._connected = True
    
    def disconnect(self):
        """Disconnect from the MCP server."""
        if self._connected and self.client:
            self.loop.run_until_complete(self.client.disconnect())
            self._connected = False
    
    def list_tools(self) -> List[Any]:
        """
        List available tools (sync).
        
        Returns:
            List of tool definitions
        """
        if not self._connected:
            raise RuntimeError("Not connected to MCP server. Call connect() first.")
        
        return self.loop.run_until_complete(self.client.list_tools_async())
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[Any]:
        """
        Call a tool (sync).
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self._connected:
            raise RuntimeError("Not connected to MCP server. Call connect() first.")
        
        return self.loop.run_until_complete(
            self.client.call_tool_async(tool_name, arguments)
        )
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        # Don't close the loop here, let Python handle it