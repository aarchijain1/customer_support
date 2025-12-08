# mcp_server/__init__.py
"""
MCP Server package for customer support operations.
"""

from .server import CustomerSupportMCPServer
from .tools import get_tool_definitions, execute_tool
from .mock_data import db, MockDatabase

__all__ = [
    'CustomerSupportMCPServer',
    'get_tool_definitions',
    'execute_tool',
    'db',
    'MockDatabase'
]