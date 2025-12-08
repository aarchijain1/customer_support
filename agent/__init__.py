# agent/__init__.py
"""
Agent package for customer support system.
"""

from .claude_agent import CustomerSupportAgent, AgentSession
from .config import Config
from .mcp_client import MCPClient, SyncMCPClient

__all__ = [
    'CustomerSupportAgent',
    'AgentSession',
    'Config',
    'MCPClient',
    'SyncMCPClient'
]