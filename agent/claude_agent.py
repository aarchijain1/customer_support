# agent/claude_agent.py
"""
Claude SDK Agent implementation for customer support.
Handles conversation flow and MCP tool integration.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from anthropic.types import Message, MessageParam, ToolUseBlock, TextBlock

from .config import Config

logger = logging.getLogger(__name__)


class CustomerSupportAgent:
    """
    Claude-powered customer support agent that uses MCP tools.
    """
    
    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            user_id: Optional user ID for the session
        """
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.user_id = user_id or Config.DEFAULT_USER_ID
        self.conversation_history: List[MessageParam] = []
        self.mcp_tools = []
        
        logger.info(f"Agent initialized for user: {self.user_id}")
    
    def set_mcp_tools(self, tools: List[Dict[str, Any]]):
        """
        Set the available MCP tools for the agent.
        
        Args:
            tools: List of tool definitions from MCP server
        """
        self.mcp_tools = tools
        logger.info(f"Loaded {len(tools)} MCP tools")
    
    def _add_to_history(self, role: str, content: Any):
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def process_message(self, user_message: str, execute_tools_callback) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            user_message: The user's input message
            execute_tools_callback: Callback function to execute MCP tools
            
        Returns:
            The agent's response string
        """
        logger.info(f"Processing user message: {user_message[:100]}...")
        
        # Add user message to history
        self._add_to_history("user", user_message)
        
        # Initial API call
        response = self._call_claude(self.conversation_history)
        
        # Handle tool use loop
        while self._has_tool_use(response):
            logger.info("Response contains tool use, processing tools...")
            
            # Add assistant's response to history
            self._add_to_history("assistant", response.content)
            
            # Execute all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info(f"Executing tool: {block.name}")
                    result = execute_tools_callback(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add tool results to history
            self._add_to_history("user", tool_results)
            
            # Continue conversation with tool results
            response = self._call_claude(self.conversation_history)
        
        # Extract final text response
        final_response = self._extract_text_response(response)
        
        # Add final response to history
        self._add_to_history("assistant", final_response)
        
        logger.info("Message processing complete")
        return final_response
    
    def _call_claude(self, messages: List[MessageParam]) -> Message:
        """
        Make an API call to Claude.
        
        Args:
            messages: Conversation history
            
        Returns:
            Claude's response
        """
        try:
            response = self.client.messages.create(
                model=Config.MODEL_NAME,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                system=Config.get_system_prompt(),
                messages=messages,
                tools=self.mcp_tools if self.mcp_tools else None
            )
            return response
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise
    
    def _has_tool_use(self, response: Message) -> bool:
        """Check if the response contains tool use blocks."""
        return any(block.type == "tool_use" for block in response.content)
    
    def _extract_text_response(self, response: Message) -> str:
        """Extract text content from Claude's response."""
        text_parts = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
        return "\n".join(text_parts) if text_parts else "I apologize, but I couldn't generate a response."
    
    def reset_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def get_conversation_history(self) -> List[MessageParam]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def set_user_id(self, user_id: str):
        """Update the user ID for the session."""
        self.user_id = user_id
        logger.info(f"User ID updated to: {user_id}")


class AgentSession:
    """
    Manages an agent session with MCP server connection.
    """
    
    def __init__(self, mcp_client, user_id: Optional[str] = None):
        """
        Initialize an agent session.
        
        Args:
            mcp_client: Connected MCP client instance
            user_id: Optional user ID for the session
        """
        self.agent = CustomerSupportAgent(user_id)
        self.mcp_client = mcp_client
        
        # Load tools from MCP server
        self._load_tools()
    
    def _load_tools(self):
        """Load available tools from MCP server."""
        try:
            tools = self.mcp_client.list_tools()
            # Convert MCP tools to Anthropic format
            anthropic_tools = [self._convert_tool_format(tool) for tool in tools]
            self.agent.set_mcp_tools(anthropic_tools)
            logger.info(f"Loaded {len(anthropic_tools)} tools from MCP server")
        except Exception as e:
            logger.error(f"Failed to load tools: {str(e)}")
            raise
    
    def _convert_tool_format(self, mcp_tool) -> Dict[str, Any]:
        """
        Convert MCP tool format to Anthropic tool format.
        
        Args:
            mcp_tool: Tool definition from MCP server
            
        Returns:
            Tool definition in Anthropic format
        """
        return {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "input_schema": mcp_tool.inputSchema
        }
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool via MCP client.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result as string
        """
        # Inject user_id if not provided and tool requires it
        if "user_id" not in arguments and self.agent.user_id:
            arguments["user_id"] = self.agent.user_id
        
        try:
            result = self.mcp_client.call_tool(tool_name, arguments)
            # Extract text from TextContent
            if isinstance(result, list) and len(result) > 0:
                return result[0].text
            return str(result)
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {tool_name}"
            })
    
    def chat(self, user_message: str) -> str:
        """
        Process a user message and return response.
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response
        """
        return self.agent.process_message(user_message, self._execute_tool)
    
    def reset(self):
        """Reset the conversation."""
        self.agent.reset_conversation()
    
    def set_user_id(self, user_id: str):
        """Update the user ID for the session."""
        self.agent.set_user_id(user_id)