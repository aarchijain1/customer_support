# agent/config.py
"""
Configuration management for the Claude agent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Configuration settings for the agent."""
    
    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    # MCP Server settings
    MCP_SERVER_HOST: str = os.getenv('MCP_SERVER_HOST', 'localhost')
    MCP_SERVER_PORT: int = int(os.getenv('MCP_SERVER_PORT', '8000'))
    
    # Agent settings
    MODEL_NAME: str = os.getenv('MODEL_NAME', 'claude-sonnet-4-20250514')
    MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', '4096'))
    TEMPERATURE: float = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Session management
    DEFAULT_USER_ID: str = os.getenv('DEFAULT_USER_ID', 'user_001')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required. Set it in .env file.")
        return True
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for the agent."""
        return """You are a helpful customer support assistant. You help customers with various account-related tasks such as:

- Changing passwords
- Checking account balances
- Updating addresses
- Viewing recent transactions
- Deactivating cards for security
- Reporting issues
- Getting account details

You should:
1. Be friendly, professional, and empathetic
2. Confirm sensitive actions before executing them
3. Provide clear feedback about what actions were taken
4. Ask for clarification when needed
5. Handle errors gracefully and inform the user

IMPORTANT: The user is already authenticated and their user_id is automatically provided to all tools. You do NOT need to ask for user_id - just use the tools directly. When a user asks "what's my balance?" or "show my transactions", immediately call the appropriate tool without asking for user_id."""


# Validate configuration on import
Config.validate()