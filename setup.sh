#!/bin/bash
set -e

SKILL_DIR="$HOME/.claude/skills/markitdown-mcp"
cd "$SKILL_DIR"

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing database..."
python -c "from src.database import init_db; init_db(); print('DB ready')"

echo "Done. Run: python mcp_server.py"
