# Customer Support Assistant System

A complete end-to-end customer support system powered by Claude AI and Model Context Protocol (MCP).

## 🏗️ Architecture

```
┌─────────────────┐
│   AGUI Client   │ ← Frontend (Future Integration)
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  Claude Agent   │ ← Python SDK
│   (Python)      │
└────────┬────────┘
         │ MCP Protocol (stdio)
┌────────▼────────┐
│   MCP Server    │ ← Tool Provider
└────────┬────────┘
         │
┌────────▼────────┐
│  Mock Database  │ ← Can be replaced with real DB
└─────────────────┘
```

## 🚀 Features

### Customer Support Operations
- **Password Management**: Change user passwords securely
- **Account Balance**: Check current account balance
- **Address Updates**: Update customer addresses
- **Transaction History**: View recent transactions
- **Card Management**: Deactivate cards for security
- **Issue Reporting**: Create support tickets
- **Account Details**: Retrieve comprehensive account information

### Technical Features
- **MCP Integration**: Full Model Context Protocol support
- **Claude SDK**: Powered by Anthropic's Claude AI
- **Tool Calling**: Automatic tool selection and execution
- **Conversation Memory**: Maintains context across interactions
- **Error Handling**: Robust error management
- **Logging**: Comprehensive logging system
- **Mock Data**: Built-in test data for development

## 📋 Prerequisites

- Python 3.10 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- pip package manager

## 🔧 Installation

### 1. Clone or Create Project Structure

```bash
mkdir customer-support-system
cd customer-support-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
DEFAULT_USER_ID=user_001
```

## 🏃 Running the System

### Test the System

First, run the test suite to ensure everything is working:

```bash
python tests/test_system.py
```

You should see all tests passing ✅

### Run Interactive Mode

Start the interactive CLI:

```bash
python run_system.py
```

## 💬 Usage Examples

### Interactive Commands

```
You: What's my account balance?
Assistant: Your current account balance is $5,420.50.

You: Change my password to newSecurePass123
Assistant: Your password has been changed successfully.

You: Show me my recent transactions
Assistant: Here are your recent transactions:
1. Amazon Purchase - $89.99 (Yesterday)
2. Salary Deposit - $3,500.00 (3 days ago)
...

You: user user_002
✓ Switched to user: user_002

You: reset
✓ Conversation reset
```

### Programmatic Usage

```python
from agent.mcp_client import SyncMCPClient
from agent.claude_agent import AgentSession

# Connect to MCP server
with SyncMCPClient("mcp_server/server.py") as mcp_client:
    # Create agent session
    session = AgentSession(mcp_client, user_id="user_001")
    
    # Chat with the agent
    response = session.chat("What's my balance?")
    print(response)
```

## 🧪 Testing

### Run All Tests

```bash
python tests/test_system.py
```

### Test Individual Components

```python
# Test mock database
from mcp_server.mock_data import db
user = db.get_user("user_001")
print(user)

# Test MCP tools
from mcp_server.tools import execute_tool
import asyncio

result = asyncio.run(execute_tool("get_account_balance", {
    "user_id": "user_001"
}))
print(result)
```

## 🔌 Frontend Integration

For the AGUI team to integrate with this backend:

### Option 1: HTTP/REST API Wrapper (Recommended)

Create a FastAPI wrapper around the agent:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize session (cache this in production)
        with SyncMCPClient("mcp_server/server.py") as mcp_client:
            session = AgentSession(mcp_client, request.user_id)
            response = session.chat(request.message)
            return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Option 2: WebSocket for Real-time Communication

```python
from fastapi import WebSocket

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    with SyncMCPClient("mcp_server/server.py") as mcp_client:
        session = AgentSession(mcp_client, user_id)
        
        while True:
            message = await websocket.receive_text()
            response = session.chat(message)
            await websocket.send_text(response)
```

### API Endpoints to Implement

```
POST   /api/chat              - Send a message to the agent
POST   /api/reset             - Reset conversation
GET    /api/history/{user_id} - Get conversation history
PUT    /api/user/{user_id}    - Switch user context
```

## 🛠️ Adding New Tools

To add a new customer support operation:

### 1. Add Tool Definition (`mcp_server/tools.py`)

```python
class NewOperationArgs(BaseModel):
    user_id: str = Field(description="User ID")
    # Add your parameters

# Add to get_tool_definitions()
Tool(
    name="new_operation",
    description="Description of what this does",
    inputSchema=NewOperationArgs.model_json_schema()
)

# Add to execute_tool()
elif tool_name == "new_operation":
    args = NewOperationArgs(**arguments)
    result = db.new_operation(args.user_id, ...)
```

### 2. Implement in Mock Database (`mcp_server/mock_data.py`)

```python
def new_operation(self, user_id: str, ...) -> Any:
    """Your implementation."""
    if user_id in self.users:
        # Your logic here
        return True
    return False
```

### 3. Test It

```python
# Test in tests/test_system.py
result = await execute_tool("new_operation", {
    "user_id": "user_001",
    # your params
})
```

## 🔐 Security Best Practices

### API Key Management

- ✅ **DO**: Use `.env` file (gitignored)
- ✅ **DO**: Use environment variables in production
- ❌ **DON'T**: Hardcode API keys
- ❌ **DON'T**: Commit `.env` to version control

### Password Handling

- ✅ **DO**: Hash passwords before storing (implement proper hashing)
- ✅ **DO**: Use HTTPS in production
- ❌ **DON'T**: Store plain text passwords
- ❌ **DON'T**: Log sensitive information

### User Authentication

For production, implement:
- JWT tokens for session management
- Rate limiting
- Input validation
- SQL injection prevention (when using real DB)
- CORS configuration

## 📊 Monitoring & Logging

Logs are written to console with timestamps:

```
2024-01-15 10:30:15 - agent.claude_agent - INFO - Processing user message
2024-01-15 10:30:16 - mcp_server.tools - INFO - Executing tool: get_account_balance
```

Configure log level in `.env`:
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY is required"

**Solution**: Create `.env` file with your API key

### "Not connected to MCP server"

**Solution**: Ensure MCP server files exist and dependencies are installed

### "Module not found"

**Solution**: Install dependencies: `pip install -r requirements.txt`

### Import Errors

**Solution**: Run from project root, not from subdirectories

### Tool Execution Fails

**Solution**: Check logs for specific error, verify tool arguments

## 📦 Project Structure

```
customer-support-system/
├── agent/                    # Claude agent implementation
│   ├── __init__.py
│   ├── claude_agent.py      # Main agent logic
│   ├── config.py            # Configuration
│   ├── mcp_client.py        # MCP client
│   └── utils.py
├── mcp_server/              # MCP server implementation
│   ├── __init__.py
│   ├── server.py            # MCP server
│   ├── tools.py             # Tool definitions
│   └── mock_data.py         # Mock database
├── tests/                   # Test suite
│   └── test_system.py
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template
├── requirements.txt         # Dependencies
├── README.md               # This file
└── run_system.py           # Main entry point
```

## 🚢 Production Deployment

### Replace Mock Database

```python
# In mock_data.py, replace MockDatabase with:
import psycopg2  # or your DB library

class ProductionDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
```

### Add Authentication

```python
# In agent session
def authenticate_user(self, user_id: str, token: str) -> bool:
    # Verify JWT token
    # Check user permissions
    pass
```

### Deploy as Service

Use systemd, Docker, or cloud services:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run_system.py"]
```

## 📚 Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude SDK](https://github.com/anthropics/anthropic-sdk-python)

## 🤝 Contributing

To extend this system:

1. Add new tools in `mcp_server/tools.py`
2. Update mock data in `mcp_server/mock_data.py`
3. Add tests in `tests/test_system.py`
4. Update documentation

## 📄 License

This is a demonstration project. Adapt as needed for your use case.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for specific errors
3. Verify configuration in `.env`
4. Ensure all dependencies are installed

---

**Built with ❤️ using Claude AI and Model Context Protocol**
