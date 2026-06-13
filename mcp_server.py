import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

from src.converters import convert_to_markdown, validate_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("markitdown-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="process_document",
            description="Convert a document (PDF, DOCX, XLSX, PPTX, HTML, TXT, MD) to Markdown.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the document"},
                },
                "required": ["file_path"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    import json

    try:
        if name == "process_document":
            file_path = arguments["file_path"]
            filename = Path(file_path).name

            is_valid, error = validate_file(file_path)
            if not is_valid:
                return [TextContent(type="text", text=json.dumps({"status": "error", "error_message": error}))]

            markdown, error = convert_to_markdown(file_path)
            if error:
                return [TextContent(type="text", text=json.dumps({"status": "error", "error_message": error}))]

            result = {
                "filename": filename,
                "markdown": markdown,
                "markdown_size_bytes": len(markdown.encode()),
            }
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "error_message": str(e)}))]


async def main() -> None:
    logger.info("markitdown-mcp server started")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
