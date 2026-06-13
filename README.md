# markitdown-mcp

MCP server that converts documents to Markdown and stores them locally.

## Tools

| Tool | Description |
|------|-------------|
| `process_document` | Convert a file to Markdown. Supports PDF, DOCX, XLSX, PPTX, HTML, TXT, MD |
| `get_markdown` | Retrieve stored Markdown by `file_id` |
| `list_documents` | List processed documents |
| `search_summaries` | Keyword search across stored Markdown content |
| `get_summary` | Metadata for a processed document |

## Requirements

- Python 3.11+
- Dependencies in `requirements.txt`

## Installation

```bash
bash setup.sh
```

## Structure

```
markitdown-mcp/
├── mcp_server.py       # MCP server (stdio)
├── src/
│   ├── converters.py   # Conversion with markitdown
│   ├── database.py     # SQLite (SQLAlchemy)
│   ├── models.py       # ORM models
│   ├── schemas.py      # Pydantic schemas
│   └── tools.py        # Tool implementations
├── requirements.txt
└── setup.sh
```

## Cache

The server calculates an MD5 hash of each file. If the same file is processed twice, it returns the cached result without reprocessing.

Markdown files are stored in `~/.claude/skills/markitdown-mcp/data/cache/`.
