# mcp_server/mock_data.py
"""
Mock database for customer support system.
In production, replace with actual database connections.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

class MockDatabase:
    """Simulates a customer database with support operations."""
    
    def __init__(self):
        self.users = {
            "user_001": {
                "user_id": "user_001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "hashed_password_123",
                "address": "123 Main St, Springfield, IL 62701",
                "account_balance": 5420.50,
                "card_status": "active",
                "card_number": "**** **** **** 1234",
                "phone": "+1-555-0123"
            },
            "user_002": {
                "user_id": "user_002",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "password": "hashed_password_456",
                "address": "456 Oak Ave, Portland, OR 97201",
                "account_balance": 12750.25,
                "card_status": "active",
                "card_number": "**** **** **** 5678",
                "phone": "+1-555-0456"
            }
        }
        
        self.transactions = {
            "user_001": [
                {
                    "id": "txn_001",
                    "date": (datetime.now() - timedelta(days=1)).isoformat(),
                    "description": "Amazon Purchase",
                    "amount": -89.99,
                    "balance": 5420.50
                },
                {
                    "id": "txn_002",
                    "date": (datetime.now() - timedelta(days=3)).isoformat(),
                    "description": "Salary Deposit",
                    "amount": 3500.00,
                    "balance": 5510.49
                },
                {
                    "id": "txn_003",
                    "date": (datetime.now() - timedelta(days=5)).isoformat(),
                    "description": "Electric Bill",
                    "amount": -125.50,
                    "balance": 2010.49
                }
            ],
            "user_002": [
                {
                    "id": "txn_004",
                    "date": (datetime.now() - timedelta(days=2)).isoformat(),
                    "description": "Grocery Store",
                    "amount": -156.32,
                    "balance": 12750.25
                }
            ]
        }
        
        self.issues = []
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password."""
        if user_id in self.users:
            self.users[user_id]["password"] = f"hashed_{new_password}"
            return True
        return False
    
    def get_account_balance(self, user_id: str) -> Optional[float]:
        """Get account balance."""
        user = self.users.get(user_id)
        return user["account_balance"] if user else None
    
    def update_address(self, user_id: str, new_address: str) -> bool:
        """Update user address."""
        if user_id in self.users:
            self.users[user_id]["address"] = new_address
            return True
        return False
    
    def get_recent_transactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions."""
        return self.transactions.get(user_id, [])[:limit]
    
    def deactivate_card(self, user_id: str) -> bool:
        """Deactivate user's card."""
        if user_id in self.users:
            self.users[user_id]["card_status"] = "deactivated"
            return True
        return False
    
    def report_issue(self, user_id: str, issue_description: str) -> str:
        """Report a customer issue."""
        issue_id = f"issue_{len(self.issues) + 1:03d}"
        issue = {
            "issue_id": issue_id,
            "user_id": user_id,
            "description": issue_description,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "priority": random.choice(["low", "medium", "high"])
        }
        self.issues.append(issue)
        return issue_id
    
    def get_account_details(self, user_id: str) -> Optional[Dict]:
        """Get full account details."""
        user = self.users.get(user_id)
        if user:
            return {
                "name": user["name"],
                "email": user["email"],
                "address": user["address"],
                "phone": user["phone"],
                "account_balance": user["account_balance"],
                "card_status": user["card_status"],
                "card_number": user["card_number"]
            }
        return None

# Global database instance
db = MockDatabase()