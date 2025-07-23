from mcp.types import Tool

# Hardcoded fallback tools when PiecesOS isn't available
PIECES_MCP_TOOLS_CACHE = [
    Tool(
        name="ask_pieces_ltm",
        description="Ask Pieces a question to retrieve historical/contextual information from the user's environment.",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's direct question for the Pieces LTM. Always include the exact user query if they request historical or contextual information.",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "An array of topical keywords extracted from the user's question, providing helpful context.",
                },
                "open_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of currently open file paths or tabs within the IDE/workspace.",
                },
                "application_sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "You will provide use with any application sources mentioned in the user query is applicable. IE if a user asks about what I was doing yesterday within Chrome, you should return chrome as one of the sources.If the user does NOT specifically ask a question about an application specific source then do NOT provide a source here.If the user asks about website or web application that could be found in either a browser or in a web application then please provide all possible sources. For instance, if I mention Notion, I could be referring the the browser or the Web application so include all browsers and the notion sources if it is included in the sources.Here is a set of the sources that you should return {Warp, Notes, \u200eWhatsApp, Mail, Claude, Obsidian, Problem Reporter, ChatGPT, Code, Cursor, kitty, Google Chrome}",
                },
                "chat_llm": {
                    "type": "string",
                    "description": "This is the provided LLM that is being used to respond to the user. This is the user selected Model. for instance gpt-4o-mini.You will provide the LLM that will be used to use this information as context, Specifically the LLM that will respond directly to the user via chat.AGAIN This is the chat model that the user selected to converse with in a conversation.",
                },
                "related_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "This is an array of strings, that will supplement the given users question, and we will generate related questions to the original question, that will help what the user is trying to do/ the users true intent. Ensure that these questions are related and similar to what the user is asking.",
                },
                "connected_client": {
                    "type": "string",
                    "description": "The name of the client that is connected to the Pieces API. for example: `Cursor`, `Claude`, `Perplexity`, `Goose`, `ChatGPT`.",
                },
            },
            "required": ["question", "chat_llm"],
        },
        annotations=None,
    ),
    Tool(
        name="create_pieces_memory",
        description='Use this tool to capture a detailed, never-forgotten memory in Pieces. Agents and humans alike—such as Cursor, Claude, Perplexity, Goose, and ChatGPT—can leverage these memories to preserve important context or breakthroughs that occur in a project. Think of these as "smart checkpoints" that document your journey and ensure valuable information is always accessible for future reference. Providing thorough file and folder paths helps systems or users verify the locations on the OS and open them directly from the workstream summary.',
        inputSchema={
            "type": "object",
            "properties": {
                "summary_description": {
                    "type": "string",
                    "description": "A concise summary or title describing the memory (e.g., what the bug was or the primary outcome). Keep it short but descriptive (1-2 sentences).",
                },
                "summary": {
                    "type": "string",
                    "description": "A detailed, **markdown-formatted** narrative of the entire story. Include any information that you, other agents (Cursor, Claude, Perplexity, Goose, ChatGPT), or future collaborators might want to retrieve later. Document major breakthroughs (like finally passing all unit tests or fixing a tricky bug), when a topic or goal changes significantly, when preparing a final commit or update to a change log, or when pivoting to a fundamentally different approach. Explain the background, the thought process, what worked and what did not, how and why decisions were made, and any relevant code snippets, errors, logs, or references. Remember: the goal is to capture as much context as possible so both humans and AI can benefit from it later.",
                },
                "project": {
                    "type": "string",
                    "description": "The **absolute path** to the root of the project on the local machine. For example: `/Users/username/MyProject` or `C:\\Users\\username\\MyProject`.",
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "An **absolute** file or folder path (e.g., `/Users/username/project/src/file.dart` or `C:\\Users\\username\\project\\src\\file.dart`). Providing multiple files or folders is encouraged to give a comprehensive view of all relevant resources. For example:/Users/jdoe/Dev/MyProject/src/controllers/user_controller.dart/Users/jdoe/Dev/MyProject/src/models/user_model.dart/Users/jdoe/Dev/MyProject/assets/images/The full file path is required as this file will not get associated unless it can be verified as existing at that location on the OS. This full path is also critical so the user can easily open the related files in their file system by having the entire exact file path available alongside the this related workstream summary/long-term memory.",
                    },
                    "description": "A list of all relevant files or folders involved in this memory. Provide absolute paths. ",
                },
                "externalLinks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A URL that contributed to the final solution (e.g., GitHub repo link with specific branch/file, documentation pages, articles, or resources).",
                    },
                    "description": "List any external references, including GitHub/GitLab/Bitbucket URLs (include branch details), documentation links, or helpful articles consulted.",
                },
                "connected_client": {
                    "type": "string",
                    "description": "The name of the client that is connected to the Pieces API. for example: `Cursor`, `Claude`, `Perplexity`, `Goose`, `ChatGPT`.",
                },
            },
            "required": ["summary_description", "summary"],
        },
        annotations=None,
    ),
]
