import importlib
import logging
import os

from agency_swarm.tools import BaseTool

logger = logging.getLogger(__name__)


def load_tools():
    tools = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(current_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"voice_assistant.tools.{module_name}")
            for name, obj in module.__dict__.items():
                if (
                    isinstance(obj, type)
                    and issubclass(obj, BaseTool)
                    and obj != BaseTool
                ):
                    tools.append(obj)
    return tools


def prepare_tool_schemas():
    """Prepare the schemas for the tools."""
    tool_schemas = []
    for tool in TOOLS:
        tool_schema = {k: v for k, v in tool.openai_schema.items() if k != "strict"}
        tool_type = "function" if not hasattr(tool, "type") else tool.type
        tool_schemas.append({**tool_schema, "type": tool_type})

    logger.debug("Tool Schemas:\n%s", tool_schemas)
    return tool_schemas


# Load all tools
TOOLS: list[BaseTool] = load_tools()
TOOL_SCHEMAS = prepare_tool_schemas()
