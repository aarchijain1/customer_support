# tests/test_system.py
"""
Test script for the customer support system.
Tests both MCP server tools and agent integration.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.mock_data import db
from mcp_server.tools import execute_tool
import asyncio


def test_mock_database():
    """Test the mock database operations."""
    print("\n" + "="*60)
    print("Testing Mock Database")
    print("="*60)
    
    # Test get_user
    user = db.get_user("user_001")
    assert user is not None, "User should exist"
    print(f"✓ Get user: {user['name']}")
    
    # Test change_password
    success = db.change_password("user_001", "new_password")
    assert success, "Password change should succeed"
    print("✓ Password changed successfully")
    
    # Test get_account_balance
    balance = db.get_account_balance("user_001")
    assert balance is not None, "Balance should be retrieved"
    print(f"✓ Account balance: ${balance:.2f}")
    
    # Test update_address
    success = db.update_address("user_001", "New Address 123")
    assert success, "Address update should succeed"
    updated_user = db.get_user("user_001")
    assert updated_user["address"] == "New Address 123", "Address should be updated"
    print("✓ Address updated successfully")
    
    # Test get_recent_transactions
    transactions = db.get_recent_transactions("user_001")
    assert len(transactions) > 0, "Should have transactions"
    print(f"✓ Retrieved {len(transactions)} transactions")
    
    # Test deactivate_card
    success = db.deactivate_card("user_001")
    assert success, "Card deactivation should succeed"
    updated_user = db.get_user("user_001")
    assert updated_user["card_status"] == "deactivated", "Card should be deactivated"
    print("✓ Card deactivated successfully")
    
    # Test report_issue
    issue_id = db.report_issue("user_001", "Test issue")
    assert issue_id.startswith("issue_"), "Should return issue ID"
    print(f"✓ Issue reported: {issue_id}")
    
    # Test get_account_details
    details = db.get_account_details("user_001")
    assert details is not None, "Should retrieve account details"
    print(f"✓ Account details retrieved for {details['name']}")
    
    print("\n✅ All database tests passed!\n")


async def test_mcp_tools():
    """Test MCP tool execution."""
    print("\n" + "="*60)
    print("Testing MCP Tools")
    print("="*60)
    
    # Reset database state
    db.users["user_001"]["card_status"] = "active"
    
    # Test change_password tool
    result = await execute_tool("change_password", {
        "user_id": "user_001",
        "new_password": "test123"
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    print("✓ change_password tool works")
    
    # Test get_account_balance tool
    result = await execute_tool("get_account_balance", {
        "user_id": "user_001"
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    assert "balance" in result_data, "Should return balance"
    print(f"✓ get_account_balance tool works: ${result_data['balance']:.2f}")
    
    # Test update_address tool
    result = await execute_tool("update_address", {
        "user_id": "user_001",
        "new_address": "999 Test Street"
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    print("✓ update_address tool works")
    
    # Test get_recent_transactions tool
    result = await execute_tool("get_recent_transactions", {
        "user_id": "user_001",
        "limit": 5
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    assert "transactions" in result_data, "Should return transactions"
    print(f"✓ get_recent_transactions tool works: {result_data['count']} transactions")
    
    # Test deactivate_card tool
    result = await execute_tool("deactivate_card", {
        "user_id": "user_001"
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    print("✓ deactivate_card tool works")
    
    # Test report_issue tool
    result = await execute_tool("report_issue", {
        "user_id": "user_001",
        "issue_description": "Test issue from automated test"
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    assert "issue_id" in result_data, "Should return issue ID"
    print(f"✓ report_issue tool works: {result_data['issue_id']}")
    
    # Test get_account_details tool
    result = await execute_tool("get_account_details", {
        "user_id": "user_001"
    })
    result_data = json.loads(result[0].text)
    assert result_data["success"], "Tool should succeed"
    assert "details" in result_data, "Should return details"
    print("✓ get_account_details tool works")
    
    # Test with invalid user
    result = await execute_tool("get_account_balance", {
        "user_id": "invalid_user"
    })
    result_data = json.loads(result[0].text)
    assert not result_data["success"], "Should fail for invalid user"
    print("✓ Tool correctly handles invalid user")
    
    print("\n✅ All MCP tool tests passed!\n")


def test_agent_config():
    """Test agent configuration."""
    print("\n" + "="*60)
    print("Testing Agent Configuration")
    print("="*60)
    
    from agent.config import Config
    
    # Test configuration validation
    try:
        Config.validate()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    # Test system prompt
    system_prompt = Config.get_system_prompt()
    assert len(system_prompt) > 0, "System prompt should not be empty"
    assert "customer support" in system_prompt.lower(), "Should mention customer support"
    print("✓ System prompt is properly configured")
    
    print("\n✅ All configuration tests passed!\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print(" CUSTOMER SUPPORT SYSTEM - TEST SUITE")
    print("="*70)
    
    try:
        # Test configuration first
        if not test_agent_config():
            print("\n❌ Configuration tests failed. Please check your .env file.")
            return
        
        # Test mock database
        test_mock_database()
        
        # Test MCP tools
        asyncio.run(test_mcp_tools())
        
        print("\n" + "="*70)
        print(" 🎉 ALL TESTS PASSED! System is ready to use.")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python run_system.py")
        print("2. Or run examples: python run_system.py --examples")
        print()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()