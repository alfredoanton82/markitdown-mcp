import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

from src.database import init_db
from src.tools import get_markdown, get_summary, list_documents, process_document, search_summaries

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".claude/skills/markitdown-mcp/data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

server = Server("markitdown-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="process_document",
            description="Convert a document (PDF, DOCX, XLSX, PPTX, HTML, TXT, MD) to Markdown and store locally.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the document"},
                    "store_in_db": {"type": "boolean", "default": True, "description": "Save result to local database"},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="get_markdown",
            description="Retrieve the stored markdown content for a previously processed document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Document ID returned by process_document"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="list_documents",
            description="List all locally processed documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10, "description": "Max number of results"},
                    "offset": {"type": "integer", "default": 0, "description": "Pagination offset"},
                },
            },
        ),
        Tool(
            name="search_summaries",
            description="Search across stored markdown content by keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "default": 5, "description": "Max number of results"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_summary",
            description="Get metadata for a processed document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Document ID"},
                },
                "required": ["file_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    import json

    try:
        if name == "process_document":
            result = process_document(
                file_path=arguments["file_path"],
                store_in_db=arguments.get("store_in_db", True),
            )
        elif name == "get_markdown":
            result = get_markdown(file_id=arguments["file_id"])
        elif name == "list_documents":
            result = list_documents(
                limit=arguments.get("limit", 10),
                offset=arguments.get("offset", 0),
            )
        elif name == "search_summaries":
            result = search_summaries(
                query=arguments["query"],
                limit=arguments.get("limit", 5),
            )
        elif name == "get_summary":
            result = get_summary(file_id=arguments["file_id"])
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "error_message": str(e)}))]


async def main() -> None:
    init_db()
    logger.info("NotebookLM MCP Server started")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
