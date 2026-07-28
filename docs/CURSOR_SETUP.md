# Cursor IDE Setup for VirtualDJ-MCP

## Prerequisites

- Cursor IDE installed
- VirtualDJ running with Network Control Plugin enabled
- Python 3.12+ with virtualdj-mcp installed

## Configuration

Add to your Cursor MCP configuration file (`.cursor/mcp.json` in your project, or global `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/virtualdj-mcp", "virtualdj-mcp"],
      "env": {
        "VDJ_HTTP_HOST": "127.0.0.1",
        "VDJ_HTTP_PORT": "80",
        "VDJ_TOOL_MODE": "portmanteau",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Alternative: system Python path

If Cursor doesn't resolve `uv`, use the full Python path:

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": ["-m", "virtualdj_mcp.__main__"],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src",
        "PYTHONUNBUFFERED": "1",
        "VDJ_HTTP_HOST": "127.0.0.1",
        "VDJ_HTTP_PORT": "80",
        "VDJ_TOOL_MODE": "portmanteau"
      }
    }
  }
}
```

## Verify

1. Open Cursor
2. Open Command Palette (Ctrl+Shift+P)
3. Run `MCP: List Servers`
4. Confirm `virtualdj-mcp` shows as connected
5. Try a test command: `vdj_system("connection_test")`

## Troubleshooting

**"Server not found"**: Ensure `uv run virtualdj-mcp` works from the repo directory first.

**"Connection refused"**: Make sure VirtualDJ is running and the Network Control Plugin is enabled in Settings > Extensions > Effects > Other > Network Control.

**Python version mismatch**: Cursor uses the system Python. Ensure `python --version` shows 3.12+.
