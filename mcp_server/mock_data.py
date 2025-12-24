# mcp_server/mock_data.py
"""
Mock database for customer support system.
Changes are now persistent - saved to a JSON file.
In production, replace with actual database connections.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import json
import sys
from pathlib import Path

class MockDatabase:
    """Simulates a customer database with support operations."""
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "database.json"
        self.load_data()
    
    def _log(self, message: str):
        """Log to stderr to avoid interfering with stdio MCP protocol."""
        print(message, file=sys.stderr)
    
    def load_data(self):
        """Load data from file if it exists, otherwise use defaults."""
        if self.data_file.exists():
            self._log(f"[DB] Loading data from {self.data_file}")
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.users = data.get('users', {})
                self.transactions = data.get('transactions', {})
                self.issues = data.get('issues', [])
            self._log(f"[DB] Loaded {len(self.users)} users, {len(self.issues)} issues")
        else:
            self._log("[DB] No saved data found, using defaults")
            self._initialize_default_data()
            self.save_data()
    
    def _initialize_default_data(self):
        """Initialize with default data."""
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
    
    def save_data(self):
        """Save data to file for persistence."""
        data = {
            'users': self.users,
            'transactions': self.transactions,
            'issues': self.issues
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        self._log(f"[DB] ✓ Data saved to {self.data_file}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password - PERMANENT."""
        if user_id in self.users:
            self.users[user_id]["password"] = f"hashed_{new_password}"
            self._log(f"[DB] Password changed for {user_id}")
            self.save_data()
            return True
        return False
    
    def get_account_balance(self, user_id: str) -> Optional[float]:
        """Get account balance."""
        user = self.users.get(user_id)
        return user["account_balance"] if user else None
    
    def update_address(self, user_id: str, new_address: str) -> bool:
        """Update user address - PERMANENT."""
        if user_id in self.users:
            old_address = self.users[user_id]["address"]
            self.users[user_id]["address"] = new_address
            self._log(f"[DB] Address changed for {user_id}")
            self._log(f"     Old: {old_address}")
            self._log(f"     New: {new_address}")
            self.save_data()
            return True
        return False
    
    def get_recent_transactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions."""
        return self.transactions.get(user_id, [])[:limit]
    
    def deactivate_card(self, user_id: str) -> bool:
        """Deactivate user's card - PERMANENT."""
        if user_id in self.users:
            old_status = self.users[user_id]["card_status"]
            self.users[user_id]["card_status"] = "deactivated"
            self._log(f"[DB] Card status changed for {user_id}")
            self._log(f"     Old: {old_status}")
            self._log(f"     New: deactivated")
            self.save_data()
            return True
        return False
    
    def report_issue(self, user_id: str, issue_description: str) -> str:
        """Report a customer issue - PERMANENT."""
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
        self._log(f"[DB] Issue created: {issue_id}")
        self.save_data()
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
    
    def switch_user(self, new_user_id: str) -> Dict:
        """Switch to a different user account."""
        user = self.users.get(new_user_id)
        if user:
            self._log(f"[DB] Switching to user: {new_user_id}")
            return {
                "success": True,
                "user_id": new_user_id,
                "user_name": user["name"],
                "message": f"Switched to user: {user['name']} ({new_user_id})"
            }
        return {
            "success": False,
            "message": f"User {new_user_id} not found. Available users: {', '.join(self.users.keys())}"
        }

# Global database instance
db = MockDatabase()