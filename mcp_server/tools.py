# mcp_server/tools.py
"""
MCP tool definitions for customer support operations.
Each tool corresponds to a customer support action.
"""

from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field
import json
import logging

from .mock_data import db

logger = logging.getLogger(__name__)


class ChangePasswordArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    new_password: str = Field(description="The new password to set")


class GetAccountBalanceArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")


class UpdateAddressArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    new_address: str = Field(description="The new address to set")


class GetRecentTransactionsArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    limit: int = Field(default=10, description="Maximum number of transactions to return")


class DeactivateCardArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")


class ReportIssueArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    issue_description: str = Field(description="Description of the issue")


class GetAccountDetailsArgs(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")


def get_tool_definitions() -> list[Tool]:
    """Return all available MCP tools."""
    return [
        Tool(
            name="change_password",
            description="Change a user's password. Returns success status.",
            inputSchema=ChangePasswordArgs.model_json_schema()
        ),
        Tool(
            name="get_account_balance",
            description="Retrieve the current account balance for a user.",
            inputSchema=GetAccountBalanceArgs.model_json_schema()
        ),
        Tool(
            name="update_address",
            description="Update a user's address in the system.",
            inputSchema=UpdateAddressArgs.model_json_schema()
        ),
        Tool(
            name="get_recent_transactions",
            description="Retrieve recent transactions for a user's account.",
            inputSchema=GetRecentTransactionsArgs.model_json_schema()
        ),
        Tool(
            name="deactivate_card",
            description="Deactivate a user's card for security purposes.",
            inputSchema=DeactivateCardArgs.model_json_schema()
        ),
        Tool(
            name="report_issue",
            description="Report a customer support issue and create a ticket.",
            inputSchema=ReportIssueArgs.model_json_schema()
        ),
        Tool(
            name="get_account_details",
            description="Retrieve comprehensive account details for a user.",
            inputSchema=GetAccountDetailsArgs.model_json_schema()
        )
    ]


async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Execute a tool by name with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
        
    Returns:
        List of TextContent results
    """
    logger.info(f"Executing tool: {tool_name} with args: {arguments}")
    
    try:
        if tool_name == "change_password":
            args = ChangePasswordArgs(**arguments)
            success = db.change_password(args.user_id, args.new_password)
            result = {
                "success": success,
                "message": "Password changed successfully" if success else "User not found"
            }
            
        elif tool_name == "get_account_balance":
            args = GetAccountBalanceArgs(**arguments)
            balance = db.get_account_balance(args.user_id)
            result = {
                "success": balance is not None,
                "balance": balance,
                "message": f"Current balance: ${balance:.2f}" if balance is not None else "User not found"
            }
            
        elif tool_name == "update_address":
            args = UpdateAddressArgs(**arguments)
            success = db.update_address(args.user_id, args.new_address)
            result = {
                "success": success,
                "message": "Address updated successfully" if success else "User not found"
            }
            
        elif tool_name == "get_recent_transactions":
            args = GetRecentTransactionsArgs(**arguments)
            transactions = db.get_recent_transactions(args.user_id, args.limit)
            result = {
                "success": True,
                "transactions": transactions,
                "count": len(transactions)
            }
            
        elif tool_name == "deactivate_card":
            args = DeactivateCardArgs(**arguments)
            success = db.deactivate_card(args.user_id)
            result = {
                "success": success,
                "message": "Card deactivated successfully" if success else "User not found"
            }
            
        elif tool_name == "report_issue":
            args = ReportIssueArgs(**arguments)
            issue_id = db.report_issue(args.user_id, args.issue_description)
            result = {
                "success": True,
                "issue_id": issue_id,
                "message": f"Issue reported successfully. Ticket ID: {issue_id}"
            }
            
        elif tool_name == "get_account_details":
            args = GetAccountDetailsArgs(**arguments)
            details = db.get_account_details(args.user_id)
            result = {
                "success": details is not None,
                "details": details,
                "message": "Account details retrieved" if details else "User not found"
            }
            
        else:
            result = {
                "success": False,
                "message": f"Unknown tool: {tool_name}"
            }
        
        logger.info(f"Tool {tool_name} executed successfully")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Failed to execute {tool_name}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]