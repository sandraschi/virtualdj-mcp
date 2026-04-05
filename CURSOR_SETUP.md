# VirtualDJ MCP - Cursor IDE Setup Guide

**Quick setup guide for running VirtualDJ MCP in Cursor IDE.**

## Prerequisites

1. **Python 3.10 or 3.11** installed and in PATH (3.12+ not supported - aubio dependency)
2. **VirtualDJ 2023 or later** installed
3. **VirtualDJ Pro license** (required for Network Control Plugin)
4. **Network Control Plugin** installed and enabled in VirtualDJ
5. **VirtualDJ MCP** installed in editable mode

## Installation

**Important:** Cursor uses the system Python, so dependencies must be installed globally or in the Python that Cursor uses.

```powershell
cd d:\Dev\repos\virtualdj-mcp

# Option 1: Install in system Python (recommended for Cursor)
# Find your system Python path (usually shown in Cursor error logs)
# Example: C:\Users\sandr\AppData\Local\Programs\Python\Python310\python.exe
python -m pip install -r requirements.txt
python -m pip install -e .

# Option 2: Install in virtual environment (if using venv in config)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

**Note:** Dependencies are defined in `pyproject.toml` and `requirements.txt`. The package includes FastMCP 2.13.1+, FastAPI, and audio processing libraries.

## VirtualDJ Network Control Plugin Setup

**Critical:** The MCP server requires VirtualDJ's Network Control Plugin to be installed and enabled.

1. Open **VirtualDJ**
2. Go to **Config** → **Extensions** → **Effects** → **Other**
3. Install **"Network Control"** plugin
4. Enable it in **Master panel** → **Master Effect** → **Auto-Start**

See `docs/NETWORK_CONTROL_SETUP.md` for detailed plugin setup instructions.

## Cursor Configuration

Add to your Cursor MCP configuration file:
**Location**: `%APPDATA%\Cursor\User\globalStorage\cursor-storage\mcp_config.json`

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": [
        "-m",
        "virtualdj_mcp.__main__"
      ],
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

**Note:** Some JSON linters object to `cwd` parameter. Using `-m` module execution with `PYTHONPATH` avoids this issue.

### Using Virtual Environment

If using a virtual environment:

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "d:\\Dev\\repos\\virtualdj-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "virtualdj_mcp.__main__"
      ],
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

### Alternative: Using server.py with Absolute Path

If you prefer using `server.py` directly (avoids `cwd` which some linters reject):

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": [
        "D:/Dev/repos/virtualdj-mcp/src/virtualdj_mcp/server.py"
      ],
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

### Plex Integration (Optional)

If using Plex integration, add Plex environment variables:

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": [
        "-m",
        "virtualdj_mcp.__main__"
      ],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src",
        "PYTHONUNBUFFERED": "1",
        "VDJ_HTTP_HOST": "127.0.0.1",
        "VDJ_HTTP_PORT": "80",
        "VDJ_TOOL_MODE": "portmanteau",
        "PLEX_SERVER_URL": "http://localhost:32400",
        "PLEX_TOKEN": "your_plex_token_here"
      }
    }
  }
}
```

## Verification

1. **Check Python import:**
   ```powershell
   python -c "import sys; sys.path.insert(0, 'src'); from virtualdj_mcp.server import mcp; print('SUCCESS')"
   ```

2. **Test MCP server startup:**
   ```powershell
   python -m virtualdj_mcp.__main__
   ```
   Should start without errors and wait for JSON-RPC messages on stdin.

3. **Test VirtualDJ connection:**
   ```powershell
   curl http://127.0.0.1:80/execute -d "nop"
   ```
   Should return a response if Network Control Plugin is running.

4. **Check Cursor logs:**
   - Location: `%APPDATA%\Cursor\logs\`
   - Look for `virtualdj-mcp` in log files
   - Check for any import errors or startup failures

## Troubleshooting

### ImportError: No module named 'fastmcp' / ModuleNotFoundError: Missing dependencies

**Solution:**
1. **Critical:** Cursor uses system Python, not your current shell's Python
2. Find system Python path from Cursor error logs (e.g., `C:\Users\sandr\AppData\Local\Programs\Python\Python310\python.exe`)
3. Install dependencies in system Python:
   ```powershell
   C:\Users\sandr\AppData\Local\Programs\Python\Python310\python.exe -m pip install -r requirements.txt
   C:\Users\sandr\AppData\Local\Programs\Python\Python310\python.exe -m pip install -e .
   ```
4. Or install globally: `python -m pip install -e .` (if `python` points to system Python)

### ModuleNotFoundError: No module named 'virtualdj_mcp'

**Solution:**
1. Ensure package is installed in the Python that Cursor uses: `python -m pip install -e .`
2. Set PYTHONPATH in Cursor config: `"PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src"`
3. Use absolute path to Python executable in venv if using virtual environment

### Cannot connect to VirtualDJ

**Solution:**
1. Ensure VirtualDJ is running
2. Verify Network Control Plugin is installed and enabled
3. Check VirtualDJ is listening on port 80: `curl http://127.0.0.1:80/execute -d "nop"`
4. Verify `VDJ_HTTP_HOST` and `VDJ_HTTP_PORT` in Cursor config match VirtualDJ settings

### Server starts but tools don't appear

**Solution:**
1. Check Cursor logs for JSON-RPC errors
2. Verify FastMCP version: `pip show fastmcp` (should be >=2.13.1,<3.0.0)
3. Restart Cursor after configuration changes
4. Check VirtualDJ connection (tools require VirtualDJ to be running)

### Python Version Issues

**Solution:**
1. VirtualDJ MCP requires Python 3.10 or 3.11 (not 3.12+)
2. Verify Python version: `python --version`
3. If using Python 3.12+, install Python 3.10 or 3.11 and use that in Cursor config

## Available Tools

VirtualDJ MCP provides 12 portmanteau tools (default mode):
- **Deck Control**: `vdj_deck` - play, pause, toggle, stop, load, seek, volume, status
- **Mixing**: `vdj_mixer` - crossfader, sync, eq_high, eq_mid, eq_low, gain, filter
- **Library**: `vdj_library` - search, analyze
- **Automation**: `vdj_automation` - start, stop, status, suggest, preferences
- **Recording**: `vdj_recording` - start, stop, status, list, export, delete
- **Performance**: `vdj_performance` - metrics, stats, trends, recommendations
- **Stems**: `vdj_stems` - kill, unkill, volume, acapella, instrumental, swap, reset
- **Beatgrid**: `vdj_beatgrid` - set_bpm, tap, adjust, anchor, pitch_bend, loop, loop_roll
- **Skin**: `vdj_skin` - info, load, variation, panel, window
- **Video**: `vdj_video` - crossfader, transition, fx, text, output, karaoke, loop
- **Plex**: `vdj_plex` - search, get_path, load_from_plex, list_libraries
- **System**: `vdj_system` - status, help, connection_test

Set `VDJ_TOOL_MODE=individual` to use 62+ individual tools instead.

## Reference

- **Generalized Setup Guide**: `mcp-central-docs/docs/patterns/WEBAPP_SETUP_GUIDE.md`
- **Cursor Standards**: `mcp-central-docs/docs/ecosystem/cursor/README.md`
- **MCP Standards**: `mcp-central-docs/STANDARDS.md`
- **Project README**: `README.md`
- **Network Control Setup**: `docs/NETWORK_CONTROL_SETUP.md`
