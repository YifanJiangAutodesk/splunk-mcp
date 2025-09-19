#!/usr/bin/env python3
"""Simple MCP test script for diagnosing issues"""

import sys
import json
import os
from datetime import datetime

def main():
    print("=== MCP Test Script ===", file=sys.stderr)
    print(f"Python version: {sys.version}", file=sys.stderr)
    print(f"Working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Environment variables:", file=sys.stderr)
    for key in ['SPLUNK_HOST', 'SPLUNK_PORT', 'SPLUNK_USERNAME', 'SPLUNK_PASSWORD']:
        print(f"  {key}: {os.environ.get(key, 'NOT SET')}", file=sys.stderr)
    
    # Try importing key modules
    try:
        import splunklib.client
        print("✓ splunklib import OK", file=sys.stderr)
    except Exception as e:
        print(f"✗ splunklib import failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        from mcp.server.fastmcp import FastMCP
        print("✓ FastMCP import OK", file=sys.stderr)
    except Exception as e:
        print(f"✗ FastMCP import failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Try connecting to Splunk
    try:
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        host = os.environ.get('SPLUNK_HOST', 'localhost')
        port = os.environ.get('SPLUNK_PORT', '18089')
        username = os.environ.get('SPLUNK_USERNAME', 'admin')
        password = os.environ.get('SPLUNK_PASSWORD', 'changeme123')
        
        url = f"https://{host}:{port}/services/server/info"
        print(f"Testing connection to: {url}", file=sys.stderr)
        
        response = requests.get(url, auth=(username, password), verify=False, timeout=5)
        print(f"✓ Splunk connection OK (status: {response.status_code})", file=sys.stderr)
    except Exception as e:
        print(f"✗ Splunk connection failed: {e}", file=sys.stderr)
        # Don't exit, continue testing MCP
    
    # Simulate MCP initialization message
    init_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"Sending MCP initialize message:", file=sys.stderr)
    print(json.dumps(init_message, indent=2), file=sys.stderr)
    
    # Output initialization message to stdout (MCP protocol)
    print(json.dumps(init_message))
    sys.stdout.flush()
    
    # Wait for response
    print("Waiting for response...", file=sys.stderr)
    try:
        response_line = sys.stdin.readline()
        if response_line:
            print(f"Received response: {response_line.strip()}", file=sys.stderr)
        else:
            print("No response received", file=sys.stderr)
    except Exception as e:
        print(f"Error reading response: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
