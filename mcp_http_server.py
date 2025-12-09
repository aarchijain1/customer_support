# mcp_http_server.py
"""
MCP Server over HTTP (works reliably on Windows).
This avoids stdio transport issues.
"""

import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import asyncio

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.tools import get_tool_definitions, execute_tool

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Support MCP Server")


# Request/Response Models
class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    success: bool
    result: str


# MCP Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "server": "MCP HTTP"}


@app.get("/tools")
async def list_tools():
    """List all available tools in Anthropic format."""
    tools = get_tool_definitions()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema  # Claude API expects input_schema, not inputSchema
            }
            for tool in tools
        ]
    }


@app.post("/tools/execute", response_model=ToolCallResponse)
async def execute_tool_endpoint(request: ToolCallRequest):
    """Execute a tool."""
    try:
        logger.info(f"Executing tool: {request.name}")
        result = await execute_tool(request.name, request.arguments)
        
        # Extract text from TextContent
        result_text = result[0].text if result else "{}"
        
        return ToolCallResponse(
            success=True,
            result=result_text
        )
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Start the HTTP MCP server."""
    logger.info("Starting MCP HTTP Server on http://localhost:8765")
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")


if __name__ == "__main__":
    main()