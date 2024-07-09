import json
import pathlib
from typing import Any, Dict

import logger

TOOL_DIR = pathlib.Path(__file__).parent / "tools"

class ToolError(Exception):
    """Custom exception for tool-related errors."""
    pass

def load_tool(name: str) -> Dict[str, Any]:
    try:
        path = TOOL_DIR / f"{name}.json"
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ToolError(f"Tool file not found: {name}.json")
    except json.JSONDecodeError:
        raise ToolError(f"Invalid JSON in tool file: {name}.json")

def get_all_tools() -> Dict[str, Dict[str, Any]]:
    tools = {}
    for file in TOOL_DIR.glob("*.json"):
        tool_name = file.stem
        try:
            tools[tool_name] = load_tool(tool_name)
        except ToolError as e:
            logger.log.error(f"Error loading tool {tool_name}: {str(e)}")
    return tools

try:
    TOOLS = get_all_tools()
except Exception as e:
    logger.log.critical(f"Failed to load tools: {str(e)}")
    TOOLS = {}
