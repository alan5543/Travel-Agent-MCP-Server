# utils.py
import re
from typing import Any
from google.generativeai.types import Tool

def convert_mcp_tool_to_gemini(mcp_tool: Any) -> Tool:
    """Convert MCP tool to Gemini-compatible Tool object."""
    type_mapping = {"number": "NUMBER", "string": "STRING", "integer": "INTEGER", "boolean": "BOOLEAN"}
    properties = {}
    input_schema = mcp_tool.inputSchema
    if "properties" in input_schema and isinstance(input_schema["properties"], dict):
        for param_name, param_schema in input_schema["properties"].items():
            mcp_type_str = param_schema.get("type", "string")
            gemini_type_str = type_mapping.get(mcp_type_str, "STRING")
            properties[param_name] = {"type": gemini_type_str, "description": param_schema.get("description", "")}
    return Tool(
        function_declarations=[{
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": {
                "type": "OBJECT",
                "properties": properties,
                "required": input_schema.get("required", [])
            }
        }]
    )