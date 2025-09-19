@echo off
cd /d "D:\projs\splunk-mcp"
call venv\Scripts\activate.bat
set SPLUNK_HOST=localhost
set SPLUNK_PORT=18089
set SPLUNK_USERNAME=admin
set SPLUNK_PASSWORD=changeme123
set SPLUNK_SCHEME=https
set VERIFY_SSL=false
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
echo Starting Splunk MCP server...
python splunk_mcp.py stdio
