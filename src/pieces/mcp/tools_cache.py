"""
MCP Tools Cache Module

Provides caching functionality for MCP tools with 3-tier fallback:
1. Live tools from connected PiecesOS
2. Saved cache from previous successful connections
3. Hardcoded fallback tools
"""

import json
import os
from typing import List
import mcp.types as types
from pieces.settings import Settings


# Hardcoded fallback tools when PiecesOS isn't available
PIECES_MCP_TOOLS_CACHE = [
    {
        "name": "ask_pieces_ltm",
        "description": "Ask Pieces a question to retrieve historical/contextual information from the user's environment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "application_sources": {
                    "description": "You will provide use with any application sources mentioned in the user query is applicable. IE if a user asks about what I was doing yesterday within Chrome, you should return chrome as one of the sources.If the user does NOT specifically ask a question about an application specific source then do NOT provide a source here.If the user asks about website or web application that could be found in either a browser or in a web application then please provide all possible sources. For instance, if I mention Notion, I could be referring the the browser or the Web application so include all browsers and the notion sources if it is included in the sources.Here is a set of the sources that you should return {​WhatsApp, Mail, Claude, Obsidian, Problem Reporter, ChatGPT, Code, Cursor, kitty, Google Chrome}",
                    "type": "array",
                    "items": {"type": "string"},
                },
                "chat_llm": {
                    "description": "This is the provided LLM that is being used to respond to the user. This is the user selected Model. for instance gpt-4o-mini.You will provide the LLM that will be used to use this information as context, Specifically the LLM that will respond directly to the user via chat.AGAIN This is the chat model that the user selected to converse with in a conversation.",
                    "type": "string",
                },
                "connected_client": {
                    "description": "The name of the client that is connected to the Pieces API. for example: `Cursor`, `Claude`, `Perplexity`, `Goose`, `ChatGPT`.",
                    "type": "string",
                },
                "open_files": {
                    "description": "List of currently open file paths or tabs within the IDE/workspace.",
                    "type": "array",
                    "items": {"type": "string"},
                },
                "question": {
                    "description": "The user's direct question for the Pieces LTM. Always include the exact user query if they request historical or contextual information.",
                    "type": "string",
                },
                "related_questions": {
                    "description": "This is an array of strings, that will supplement the given users question, and we will generate related questions to the original question, that will help what the user is trying to do/ the users true intent. Ensure that these questions are related and similar to what the user is asking.",
                    "type": "array",
                    "items": {"type": "string"},
                },
                "topics": {
                    "description": "An array of topical keywords extracted from the user's question, providing helpful context.",
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["question", "chat_llm"],
        },
    },
    {
        "name": "create_pieces_memory",
        "description": 'Use this tool to capture a detailed, never-forgotten memory in Pieces. Agents and humans alike—such as Cursor, Claude, Perplexity, Goose, and ChatGPT—can leverage these memories to preserve important context or breakthroughs that occur in a project. Think of these as "smart checkpoints" that document your journey and ensure valuable information is always accessible for future reference. Providing thorough file and folder paths helps systems or users verify the locations on the OS and open them directly from the workstream summary.',
        "inputSchema": {
            "type": "object",
            "properties": {
                "connected_client": {
                    "description": "The name of the client that is connected to the Pieces API. for example: `Cursor`, `Claude`, `Perplexity`, `Goose`, `ChatGPT`.",
                    "type": "string",
                },
                "externalLinks": {
                    "description": "List any external references, including GitHub/GitLab/Bitbucket URLs (include branch details), documentation links, or helpful articles consulted.",
                    "type": "array",
                    "items": {
                        "description": "A URL that contributed to the final solution (e.g., GitHub repo link with specific branch/file, documentation pages, articles, or resources).",
                        "type": "string",
                    },
                },
                "files": {
                    "description": "A list of all relevant files or folders involved in this memory. Provide absolute paths.",
                    "type": "array",
                    "items": {
                        "description": "An **absolute** file or folder path (e.g., `/Users/username/project/src/file.dart` or `C:\\Users\\username\\project\\src\\file.dart`). Providing multiple files or folders is encouraged to give a comprehensive view of all relevant resources. For example:/Users/jdoe/Dev/MyProject/src/controllers/user_controller.dart/Users/jdoe/Dev/MyProject/src/models/user_model.dart/Users/jdoe/Dev/MyProject/assets/images/The full file path is required as this file will not get associated unless it can be verified as existing at that location on the OS. This full path is also critical so the user can easily open the related files in their file system by having the entire exact file path available alongside the this related workstream summary/long-term memory.",
                        "type": "string",
                    },
                },
                "project": {
                    "description": "The **absolute path** to the root of the project on the local machine. For example: `/Users/username/MyProject` or `C:\\Users\\username\\MyProject`.",
                    "type": "string",
                },
                "summary": {
                    "description": "A detailed, **markdown-formatted** narrative of the entire story. Include any information that you, other agents (Cursor, Claude, Perplexity, Goose, ChatGPT), or future collaborators might want to retrieve later. Document major breakthroughs (like finally passing all unit tests or fixing a tricky bug), when a topic or goal changes significantly, when preparing a final commit or update to a change log, or when pivoting to a fundamentally different approach. Explain the background, the thought process, what worked and what did not, how and why decisions were made, and any relevant code snippets, errors, logs, or references. Remember: the goal is to capture as much context as possible so both humans and AI can benefit from it later.",
                    "type": "string",
                },
                "summary_description": {
                    "description": "A concise summary or title describing the memory (e.g., what the bug was or the primary outcome). Keep it short but descriptive (1-2 sentences).",
                    "type": "string",
                },
            },
            "required": ["summary_description", "summary"],
        },
    },
]


class MCPToolsCache:
    """
    Manages caching of MCP tools with 3-tier fallback system:
    1. Live tools from connected PiecesOS
    2. Saved cache from previous successful connections
    3. Hardcoded fallback tools
    """

    def __init__(self):
        self.cache_file = os.path.join(Settings.pieces_data_dir, "mcp_tools_cache.json")

    def save_tools_cache(self, tools: List[types.Tool]) -> bool:
        """
        Save live tools to cache file for future offline use.

        Args:
            tools: List of MCP Tool objects from live connection

        Returns:
            bool: True if cache was saved successfully, False otherwise
        """
        try:
            # Ensure the data directory exists
            os.makedirs(Settings.pieces_data_dir, exist_ok=True)

            # Convert Tool objects to serializable format
            tools_data = []
            for tool in tools:
                tool_data = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
                tools_data.append(tool_data)

            # Save to cache file
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(tools_data, f, indent=2, ensure_ascii=False)

            Settings.logger.debug(
                f"Saved {len(tools_data)} tools to cache: {self.cache_file}"
            )
            return True

        except Exception as e:
            Settings.logger.error(f"Failed to save tools cache: {e}")
            return False

    def load_saved_cache(self) -> List[types.Tool]:
        """
        Load tools from saved cache file.

        Returns:
            List[types.Tool]: List of cached tools, empty list if cache doesn't exist or is invalid
        """
        try:
            if not os.path.exists(self.cache_file):
                Settings.logger.debug("No saved tools cache found")
                return []

            with open(self.cache_file, "r", encoding="utf-8") as f:
                tools_data = json.load(f)

            # Convert back to Tool objects
            tools = []
            for tool_data in tools_data:
                tool = types.Tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    inputSchema=tool_data["inputSchema"],
                )
                tools.append(tool)

            Settings.logger.debug(f"Loaded {len(tools)} tools from saved cache")
            return tools

        except Exception as e:
            Settings.logger.error(f"Failed to load saved tools cache: {e}")
            return []

    def get_hardcoded_cache(self) -> List[types.Tool]:
        """
        Get hardcoded fallback tools.

        Returns:
            List[types.Tool]: List of hardcoded fallback tools
        """
        try:
            tools = []
            for tool_data in PIECES_MCP_TOOLS_CACHE:
                tool = types.Tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    inputSchema=tool_data["inputSchema"],
                )
                tools.append(tool)

            Settings.logger.debug(f"Using {len(tools)} hardcoded fallback tools")
            return tools

        except Exception as e:
            Settings.logger.error(f"Failed to create hardcoded tools: {e}")
            return []


def get_available_tools() -> List[types.Tool]:
    """
    Get available tools using 3-tier fallback system:
    1. Try saved cache first
    2. Fall back to hardcoded cache if saved cache fails

    Returns:
        List[types.Tool]: List of available tools
    """
    cache_manager = MCPToolsCache()

    # Try saved cache first
    tools = cache_manager.load_saved_cache()
    if tools:
        Settings.logger.debug("Using saved tools cache")
        return tools

    # Fall back to hardcoded cache
    Settings.logger.debug("No saved cache available, using hardcoded fallback tools")
    return cache_manager.get_hardcoded_cache()

