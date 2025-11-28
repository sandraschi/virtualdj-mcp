# VirtualDJ-MCP 🎵

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](docs/MCP_PRODUCTION_CHECKLIST.md)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13.1-blue.svg)](https://gofastmcp.com)

Professional DJ automation MCP server with Austrian efficiency for Sandra's music mixing needs.

## 🎯 Overview

VirtualDJ-MCP provides seamless integration between Claude and VirtualDJ, enabling professional DJ automation, mixing, and library management through natural language commands.

### 📋 Capabilities (25+ Tools)

- **Deck Control**: Play/pause/stop, load tracks, seek, volume, status monitoring
- **Mixing Tools**: Crossfader control, auto-sync, beatmatching, EQ controls
- **Library Tools**: Browse library, search tracks, get track info
- **Automation**: VirtualDJ Auto-DJ, recording controls, session management
- **Performance**: Real-time monitoring, variable access, status reporting

### 💪 Strengths

- Professional DJ software integration (20+ years of VirtualDJ development)
- **HTTP API Integration**: Real-time control via Network Control Plugin
- Real-time deck control and mixing automation
- VirtualDJ's built-in Auto-DJ and recording features
- Multi-deck support (up to 8 decks simultaneously)
- Hardware controller integration through VirtualDJ
- **Production-Ready**: FastMCP 2.13.1 implementation
- **Dual Interface**: MCP (Claude Desktop/Cursor) + FastAPI (Web API)

### ⚠️ Requirements

- **VirtualDJ 2023 or later**
- **VirtualDJ Pro license** (required for Network Control Plugin)
- Python 3.11+
- Network Control Plugin installed and enabled

## 🚀 Quick Start

### Step 1: Install VirtualDJ Network Control Plugin

This is **required** for VirtualDJ-MCP to communicate with VirtualDJ.

1. Open **VirtualDJ**
2. Go to **Config** → **Extensions** → **Effects** → **Other**
3. Install **"Network Control"** plugin
4. Enable it in **Master panel** → **Master Effect** → **Auto-Start**

📖 **[Full Plugin Setup Guide](docs/NETWORK_CONTROL_SETUP.md)**

### Step 2: Install VirtualDJ-MCP

```powershell
# Clone repository
git clone https://github.com/sandraschi/virtualdj-mcp.git
cd virtualdj-mcp

# Create virtual environment
python -m venv vdj-mcp-env

# Activate environment (Windows PowerShell)
.\vdj-mcp-env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Step 3: Configure MCP Client

**For Claude Desktop** - Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": ["-m", "virtualdj_mcp.server"],
      "cwd": "D:/Dev/repos/virtualdj-mcp",
      "env": {
        "PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**For Cursor** - Add to `~/.cursor/mcp.json`:

```json
{
  "virtualdj-mcp": {
    "command": "python",
    "args": ["-m", "virtualdj_mcp.server"],
    "cwd": "D:/Dev/repos/virtualdj-mcp",
    "env": {
      "PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src",
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

### Step 4: Test Connection

```powershell
# Test HTTP API directly
python -c "import httpx; r=httpx.post('http://127.0.0.1:80/execute', content='deck 1 play', headers={'Content-Type': 'text/plain'}); print(r.status_code, r.text)"
```

Expected output: `200 true`

## Configuration

### Environment Variables

```env
# Network Control Plugin (HTTP API)
VDJ_HTTP_HOST=127.0.0.1      # Plugin host (default: 127.0.0.1)
VDJ_HTTP_PORT=80             # Plugin port (default: 80)
VDJ_HTTP_PASSWORD=           # Optional authentication password
VDJ_HTTP_TIMEOUT=10.0        # Request timeout in seconds

# VirtualDJ paths
VDJ_PATH=C:/Program Files/VirtualDJ/virtualdj.exe
VDJ_LIBRARY_PATH=C:/Music

# General settings
VDJ_DEFAULT_VOLUME=75
VDJ_MAX_DECKS=4
```

## Usage Examples

### Natural Language (via Claude/Cursor)

```
"Load the Albinoni Adagio to deck 1 and start playing"
"Set crossfader to favor deck 2"
"Auto-sync decks 1 and 2"
"Show current deck status"
"Search for techno tracks around 140 BPM"
```

### MCP Tools

```python
# Control playback
play_pause_deck(deck_id=1, action="play")

# Load tracks
load_track_to_deck(deck_id=1, track_path="E:/Music/track.mp3")

# Get status
get_deck_status(deck_id=1)

# Mixing
set_crossfader_position(position=50)  # Center
auto_sync_decks(deck_a=1, deck_b=2)
```

### FastAPI Server (Web API)

```powershell
# Start FastAPI server
$env:RUN_FASTAPI="true"
python -m virtualdj_mcp.server

# Access API documentation at: http://localhost:8000/api/docs
```

## 🎛️ Available Tools

### Deck Control
| Tool | Description |
|------|-------------|
| `play_pause_deck(deck_id, action)` | Control playback (play/pause/toggle) |
| `load_track_to_deck(deck_id, track_path)` | Load track to deck |
| `seek_deck(deck_id, position)` | Seek to position |
| `set_deck_volume(deck_id, volume)` | Set deck volume (0-100) |
| `get_deck_status(deck_id)` | Get deck status and track info |

### Mixing
| Tool | Description |
|------|-------------|
| `set_crossfader_position(position)` | Set crossfader (-100 to +100) |
| `auto_sync_decks(deck_a, deck_b)` | Sync BPM between decks |

### Library
| Tool | Description |
|------|-------------|
| `search_tracks(query, ...)` | Search music library |
| `analyze_track_audio(track_path)` | Analyze BPM, key, energy |

### Automation
| Tool | Description |
|------|-------------|
| `auto_dj_mode(...)` | Enable Auto-DJ |
| `stop_auto_dj()` | Stop Auto-DJ |
| `suggest_next_track(style)` | Get track suggestions |

### Recording
| Tool | Description |
|------|-------------|
| `start_recording(name, format)` | Start recording mix |
| `stop_recording()` | Stop recording |
| `list_recordings()` | List saved recordings |

### Performance
| Tool | Description |
|------|-------------|
| `get_performance_metrics()` | Get DJ performance metrics |
| `get_session_statistics()` | Get session analytics |
| `show_help()` | Show help documentation |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude / Cursor                          │
│                         (MCP Client)                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol (stdio)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VirtualDJ-MCP Server                       │
│                       (FastMCP 2.13.1)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Deck Tools  │  │ Mixer Tools │  │ Library/Auto/Recording  │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
│         └────────────────┼──────────────────────┘               │
│                          ▼                                      │
│              ┌─────────────────────┐                            │
│              │   VirtualDJ Client  │                            │
│              │    (HTTP/httpx)     │                            │
│              └──────────┬──────────┘                            │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP POST (localhost:80)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VirtualDJ Application                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Network Control Plugin                        │  │
│  │         /execute  │  /query                               │  │
│  └───────────────────┴───────────────────────────────────────┘  │
│                          │                                      │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────┐  │
│  │  Deck 1   │  │  Deck 2   │  │  Library  │  │   Mixer     │  │
│  └───────────┘  └───────────┘  └───────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### "Cannot connect to VirtualDJ Network Control Plugin"

1. Ensure VirtualDJ is running
2. Verify Network Control Plugin is installed and enabled
3. Check the port (default: 80) isn't blocked
4. Test directly: `curl http://127.0.0.1:80/execute -d "nop"`

### Commands return "false"

- Check VDJScript syntax
- Verify file paths exist (use forward slashes)
- Ensure deck number is valid (1-8)

### Track won't load

- Verify file path is correct and accessible
- Use forward slashes: `E:/Music/track.mp3`
- Check file format is supported by VirtualDJ

📖 **[Full Troubleshooting Guide](docs/NETWORK_CONTROL_SETUP.md#troubleshooting)**

## 🇦🇹 Austrian Efficiency

This project embodies Austrian efficiency principles:
- **Practical solutions** over theoretical complexity
- **Cultural awareness** for Vienna music scene
- **No decision paralysis** - exactly what you need, when you need it
- **Professional quality** without overwhelming options

Perfect for Sandra's DJ automation needs in Vienna!

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📚 Documentation

- **[Network Control Setup](docs/NETWORK_CONTROL_SETUP.md)** - Plugin installation and HTTP API
- **[VirtualDJ Reference](docs/VIRTUALDJ_REFERENCE.md)** - VDJScript commands
- **[FastMCP 2.13 Migration](docs/FASTMCP_2.13_MIGRATION.md)** - Migration guide
- **[MCP Production Checklist](docs/MCP_PRODUCTION_CHECKLIST.md)** - Production readiness

---

**Built with Austrian efficiency for professional DJ automation! 🎵🇦🇹**
