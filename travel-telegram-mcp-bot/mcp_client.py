# mcp_client.py
from typing import Dict, Any, List
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.generativeai.types import Tool

from config import logger
from utils import convert_mcp_tool_to_gemini

class MCPClient:
    """
    Manages connections to and interactions with MCP servers.
    """
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}  # Map server name to session
        self.gemini_tools: List[Tool] = []
        self.exit_stack = AsyncExitStack()

    async def connect(self, server_configs: List[Dict[str, Any]]) -> None:
        """Connect to multiple MCP servers and initialize tools."""
        try:
            for config in server_configs:
                server_name = config.get("name", "unnamed_server")
                logger.info("Connecting to MCP server: %s", server_name)
                server_params = StdioServerParameters(
                    command=config["command"],
                    args=config["args"],
                    env=config.get("env")
                )
                # Establish connection and session
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                stdio, stdout = stdio_transport
                session = await self.exit_stack.enter_async_context(ClientSession(stdio, stdout))
                await session.initialize()
                
                # List tools and convert them for Gemini
                response = await session.list_tools()
                self.sessions[server_name] = session
                server_tools = [convert_mcp_tool_to_gemini(tool) for tool in response.tools]
                self.gemini_tools.extend(server_tools)
                
                tool_names = [tool.function_declarations[0].name for tool in server_tools]
                logger.info("Connected to MCP server '%s'. Available tools: %s", server_name, tool_names)
        except Exception as e:
            logger.error("Failed to connect to MCP server: %s", e, exc_info=True)
            raise

    async def call_tool(self, tool_name: str, tool_args: Dict) -> Any:
        """Execute a tool on the appropriate MCP server."""
        for server_name, session in self.sessions.items():
            # Check if the tool exists on this server before calling
            tools_response = await session.list_tools()
            if any(tool.name == tool_name for tool in tools_response.tools):
                logger.info("Calling tool '%s' on server '%s' with arguments %s", tool_name, server_name, tool_args)
                return await session.call_tool(tool_name, tool_args)
        
        logger.error("Tool '%s' not found on any connected MCP server.", tool_name)
        raise RuntimeError(f"Tool '{tool_name}' not found on any connected MCP server.")

    async def cleanup(self) -> None:
        """Clean up all MCP resources gracefully."""
        if hasattr(self, 'exit_stack'):
            await self.exit_stack.aclose()
            logger.info("MCP client connections cleaned up successfully.")

