# mcp_server_fastmcp.py
"""
MCP Server using FastMCP library.
Much simpler and more reliable than raw MCP SDK.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from mcp_server.mock_data import db

# Initialize FastMCP server
mcp = FastMCP("Customer Support MCP Server")


@mcp.tool()
def change_password(user_id: str, new_password: str) -> dict:
    """
    Change a user's password. This change is permanent.
    
    Args:
        user_id: The unique identifier for the user
        new_password: The new password to set
    
    Returns:
        dict: Success status and message
    """
    success = db.change_password(user_id, new_password)
    return {
        "success": success,
        "message": "Password changed successfully and persisted" if success else "User not found"
    }


@mcp.tool()
def get_account_balance(user_id: str) -> dict:
    """
    Retrieve the current account balance for a user.
    
    Args:
        user_id: The unique identifier for the user
    
    Returns:
        dict: Success status, balance, and message
    """
    balance = db.get_account_balance(user_id)
    return {
        "success": balance is not None,
        "balance": balance,
        "message": f"Current balance: ${balance:.2f}" if balance is not None else "User not found"
    }


@mcp.tool()
def update_address(user_id: str, new_address: str) -> dict:
    """
    Update a user's address in the system. This change is permanent.
    
    Args:
        user_id: The unique identifier for the user
        new_address: The new address to set
    
    Returns:
        dict: Success status and message
    """
    success = db.update_address(user_id, new_address)
    return {
        "success": success,
        "message": "Address updated successfully and persisted" if success else "User not found"
    }


@mcp.tool()
def get_recent_transactions(user_id: str, limit: int = 10) -> dict:
    """
    Retrieve recent transactions for a user's account.
    
    Args:
        user_id: The unique identifier for the user
        limit: Maximum number of transactions to return (default: 10)
    
    Returns:
        dict: Success status, transactions list, and count
    """
    transactions = db.get_recent_transactions(user_id, limit)
    return {
        "success": True,
        "transactions": transactions,
        "count": len(transactions)
    }


@mcp.tool()
def deactivate_card(user_id: str) -> dict:
    """
    Deactivate a user's card for security purposes. This change is permanent.
    
    Args:
        user_id: The unique identifier for the user
    
    Returns:
        dict: Success status and message
    """
    success = db.deactivate_card(user_id)
    return {
        "success": success,
        "message": "Card deactivated successfully and persisted" if success else "User not found"
    }


@mcp.tool()
def report_issue(user_id: str, issue_description: str) -> dict:
    """
    Report a customer support issue and create a ticket. The ticket is permanently stored.
    
    Args:
        user_id: The unique identifier for the user
        issue_description: Description of the issue
    
    Returns:
        dict: Success status, issue ID, and message
    """
    issue_id = db.report_issue(user_id, issue_description)
    return {
        "success": True,
        "issue_id": issue_id,
        "message": f"Issue reported successfully and stored. Ticket ID: {issue_id}"
    }


@mcp.tool()
def get_account_details(user_id: str) -> dict:
    """
    Retrieve comprehensive account details for a user, including any recent updates.
    
    Args:
        user_id: The unique identifier for the user
    
    Returns:
        dict: Success status, account details, and message
    """
    details = db.get_account_details(user_id)
    return {
        "success": details is not None,
        "details": details,
        "message": "Account details retrieved (includes any updates)" if details else "User not found"
    }


@mcp.tool()
def switch_user(new_user_id: str) -> dict:
    """
    Switch to a different user account.
    
    Args:
        new_user_id: The user ID to switch to (e.g., user_001, user_002)
    
    Returns:
        dict: Success status, user info, and message
    """
    result = db.switch_user(new_user_id)
    return result


if __name__ == "__main__":
    # Run the FastMCP server
    print("=" * 60)
    print("Starting FastMCP Server...")
    print("=" * 60)
    print("\nServer is running with 8 tools")
    print("All changes are PERSISTENT (saved to database.json)")
    print("Press CTRL+C to stop\n")
    mcp.run()