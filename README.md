# markitdown-mcp

MCP server that converts documents to Markdown. Stateless — no database, no storage.

## Tool

### `process_document`

Converts a local file to Markdown and returns the content directly.

**Input**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file |

**Output**

```json
{
  "filename": "report.pdf",
  "markdown": "# Report\n...",
  "markdown_size_bytes": 4821
}
```

**Supported formats:** PDF, DOCX, XLSX, PPTX, HTML, TXT, MD

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/alfredoanton82/markitdown-mcp.git ~/.claude/skills/markitdown-mcp
cd ~/.claude/skills/markitdown-mcp
```

### 2. Create the virtual environment and install dependencies

```bash
bash setup.sh
```

---

## Add to Claude Code

Add this block to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "/Users/<your-user>/.claude/skills/markitdown-mcp/venv/bin/python",
      "args": ["/Users/<your-user>/.claude/skills/markitdown-mcp/mcp_server.py"],
      "type": "stdio"
    }
  }
}
```

**Windows paths:**

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "C:\\Users\\<your-user>\\.claude\\skills\\markitdown-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\<your-user>\\.claude\\skills\\markitdown-mcp\\mcp_server.py"],
      "type": "stdio"
    }
  }
}
```

---

## Add to Claude Desktop

Edit the Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "/Users/<your-user>/.claude/skills/markitdown-mcp/venv/bin/python",
      "args": ["/Users/<your-user>/.claude/skills/markitdown-mcp/mcp_server.py"]
    }
  }
}
```

**Windows:**

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "C:\\Users\\<your-user>\\.claude\\skills\\markitdown-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\<your-user>\\.claude\\skills\\markitdown-mcp\\mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop after editing the config.

---

## Requirements

- Python 3.10+
- No API keys or credentials needed
