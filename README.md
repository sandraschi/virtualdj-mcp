# VirtualDJ-MCP 

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

Professional DJ automation MCP server with Austrian efficiency for Sandra's music mixing needs.

## Quick Start

```powershell
git clone https://github.com/sandraschi/virtualdj-mcp
cd virtualdj-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:

##  Overview

VirtualDJ-MCP provides seamless integration between Claude and VirtualDJ, enabling professional DJ automation, mixing, and library management through natural language commands.

###  What's New (v2.0)

- **Portmanteau Tools**: 62+ tools consolidated into 12 clean interfaces (81% reduction!)
- **Plex Integration**: Search and load tracks directly from Plex Media Server
- **Stem Separation**: Real-time vocal/instrumental isolation and mashups
- **Video Mixing**: Full video DJ support with effects and transitions
- **Cross-MCP deck API**: standard REST endpoints for load/play/sync/cue handoff from other MCP servers

###  Strengths

- Professional DJ software integration (20+ years of VirtualDJ development)
- **HTTP API Integration**: Real-time control via Network Control Plugin
- Real-time deck control and mixing automation
- Multi-deck support (up to 8 decks simultaneously)
- **NEW: Plex Media Server integration**
- **Production-Ready**: FastMCP 3.1.0 implementation

###  Requirements

- **VirtualDJ 2023 or later**
- **VirtualDJ Pro license** (required for Network Control Plugin)
- **Python 3.10 or 3.11** (3.12+ not supported - aubio dependency)
- Network Control Plugin installed and enabled

##  Quick Start

### Step 1: Install VirtualDJ Network Control Plugin

1. Open **VirtualDJ**
2. Go to **Config**  **Extensions**  **Effects**  **Other**
3. Install **"Network Control"** plugin
4. Enable it in **Master panel**  **Master Effect**  **Auto-Start**

 **[Full Plugin Setup Guide](docs/NETWORK_CONTROL_SETUP.md)**

### Step 2: Install VirtualDJ-MCP

```powershell
git clone https://github.com/sandraschi/virtualdj-mcp.git
cd virtualdj-mcp
uv venv-mcp-env
.\vdj-mcp-env\Scripts\Activate.ps1
uv pip install -r requirements.txt
uv pip install -e .
```

### Step 3: Configure Claude Desktop / Cursor IDE

#### For Cursor IDE

**Important:** Cursor uses system Python. Install dependencies in the Python that Cursor uses:

```powershell
# Find system Python path (check Cursor error logs if needed)
# Example: C:\Users\sandr\AppData\Local\Programs\Python\Python310\python.exe
python -m uv pip install -r requirements.txt
python -m uv pip install -e .
```

See `CURSOR_SETUP.md` for detailed Cursor configuration instructions.

#### For Claude Desktop

Add to `claude_desktop_config.json`:

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

**Note:** Some JSON linters object to `cwd` parameter. Using `-m` module execution with `PYTHONPATH` avoids this issue.

##  Portmanteau Tools (Default)

VirtualDJ-MCP uses **12 consolidated portmanteau tools** for a cleaner AI interface:

| Tool | Operations | Description |
|------|------------|-------------|
| `vdj_deck` | play, pause, toggle, stop, load, seek, volume, status | Deck playback control |
| `vdj_mixer` | crossfader, sync, eq_high, eq_mid, eq_low, gain, filter | Mixing and EQ |
| `vdj_library` | search, analyze | Library search and audio analysis |
| `vdj_automation` | start, stop, status, suggest, preferences | Auto-DJ control |
| `vdj_recording` | start, stop, status, list, export, delete | Mix recording |
| `vdj_performance` | metrics, stats, trends, recommendations | Performance analytics |
| `vdj_stems` | kill, unkill, volume, acapella, instrumental, swap, reset | Stem separation |
| `vdj_beatgrid` | set_bpm, tap, adjust, anchor, pitch_bend, loop, loop_roll | BPM and loops |
| `vdj_skin` | info, load, variation, panel, window | Skin control |
| `vdj_video` | crossfader, transition, fx, text, output, karaoke, loop | Video mixing |
| **`vdj_plex`** | **search, get_path, load_from_plex, list_libraries** | **Plex integration** |
| `vdj_system` | status, help, connection_test | System status |

### Tool Mode

Set `VDJ_TOOL_MODE` environment variable:
- `portmanteau` (default) - 12 consolidated tools
- `individual` - 62+ individual tools (backward compatibility)

## Cross-MCP REST deck handoff

VirtualDJ-MCP exposes stable REST endpoints so other MCP servers can hand off tracks without MCP tool coupling:

- `POST /api/v1/deck/{deck_id}/load` (`track_path`)
- `POST /api/v1/deck/{deck_id}/play_pause` (`action=play|pause|toggle`)
- `POST /api/v1/deck/{deck_id}/sync`
- `POST /api/v1/deck/{deck_id}/cue` (`mode=start|cue|set_cue`)

These are used by `songgeneration-mcp` Listen exports for direct deck preparation before live mixing/scratching.


##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx virtualdj-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "virtualdj-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/virtualdj-mcp", "run", "virtualdj-mcp"]
  }
}
```

## Usage Examples

### Natural Language (via Claude)

```
"Load Dancing Queen by ABBA to deck 1 and play it"
"Search my Plex library for Pink Floyd and load to deck 2"
"Sync the decks and crossfade to 50/50"
"Put deck 1 in acapella mode - I want just the vocals"
"Create a mashup: ABBA vocals over Pink Floyd instrumental"
```

### Portmanteau Tool Examples

```python
# Basic playback
vdj_deck("load", deck_id=1, track_path="C:/Music/track.mp3")
vdj_deck("play", deck_id=1)

# Load from Plex
vdj_plex("search", query="ABBA", limit=10)
vdj_plex("load_from_plex", query="Dancing Queen", deck_id=1)
vdj_plex("load_from_plex", artist="Pink Floyd", deck_id=2)

# Mixing
vdj_mixer("sync", deck_a=1, deck_b=2)
vdj_mixer("crossfader", position=0)  # Center

# Stem mashup!
vdj_stems("swap", deck_a=1, deck_b=2, stem="vocal")  # ABBA vocals over Pink Floyd!

# Quick acapella/instrumental
vdj_stems("acapella", deck_id=1)      # Vocals only
vdj_stems("instrumental", deck_id=2)   # No vocals

# Video mixing
vdj_video("transition", transition_type="cube", duration=2.0)
vdj_video("text", text="DJ Sandra", text_position="bottom")

# Recording
vdj_recording("start", name="Friday Night Mix", format="mp3")
vdj_recording("stop")
```

##  Plex Integration

Load tracks directly from your Plex Media Server!

### Setup

Add Plex token to your environment:

```json
{
  "virtualdj-mcp": {
    "env": {
      "PLEX_SERVER_URL": "http://localhost:32400",
      "PLEX_TOKEN": "your_plex_token_here"
    }
  }
}
```


##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx virtualdj-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "virtualdj-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/virtualdj-mcp", "run", "virtualdj-mcp"]
  }
}
```

## Usage

```python
# List your music libraries
vdj_plex("list_libraries")

# Search for tracks
vdj_plex("search", query="ABBA", limit=10)
vdj_plex("search", artist="Pink Floyd")

# Load directly to deck
vdj_plex("load_from_plex", query="Dancing Queen", deck_id=1)
```

##  Stem Separation

VirtualDJ's Stems 2.0 enables real-time isolation:

| Stem | Description |
|------|-------------|
| `vocal` | Vocals |
| `instru` | Instrumental (everything except vocals) |
| `bass` | Bass frequencies |
| `drums` | Full drum kit |
| `hihat` | Hi-hats |
| `kick` | Kick drum |
| `snare` | Snare drum |
| `melody` | Melody/synths |

### Quick Modes

```python
vdj_stems("acapella", deck_id=1)       # Vocals only
vdj_stems("instrumental", deck_id=1)   # No vocals
vdj_stems("isolate_drums", deck_id=1)  # Drums only

# Mashup: vocals from deck 1, instrumental from deck 2
vdj_stems("swap", deck_a=1, deck_b=2, stem="vocal")
```

## Configuration

### Environment Variables

```env
# Network Control Plugin
VDJ_HTTP_HOST=127.0.0.1
VDJ_HTTP_PORT=80
VDJ_HTTP_PASSWORD=
VDJ_HTTP_TIMEOUT=10.0

# Tool mode
VDJ_TOOL_MODE=portmanteau  # or "individual"

# Plex integration
PLEX_SERVER_URL=http://localhost:32400
PLEX_TOKEN=your_token_here

# VirtualDJ paths
VDJ_PATH=C:/Program Files/VirtualDJ/virtualdj.exe
VDJ_LIBRARY_PATH=C:/Music
```

## Architecture

```

                        Claude / Cursor                          
                         (MCP Client)                            

                           MCP Protocol (stdio)
                          

                      VirtualDJ-MCP Server                       
                       (FastMCP 3.1.0)                          
     
                12 Portmanteau Tools                            
    vdj_deck  vdj_mixer  vdj_stems  vdj_plex  ...          
     
                                                                 
                                 
   VDJ Client        Plex Client                             
   (HTTP/httpx)      (HTTP/httpx)                            
                                 

                             
                             
    
   VirtualDJ           Plex Server    
 Network Control       (port 32400)   
   (port 80)                          
    
```

## Troubleshooting

### "Cannot connect to VirtualDJ"

1. Ensure VirtualDJ is running
2. Verify Network Control Plugin is installed and enabled
3. Test: `curl http://127.0.0.1:80/execute -d "nop"`

### "Plex connection failed"

1. Verify `PLEX_TOKEN` is set correctly
2. Test: `curl "http://localhost:32400/?X-Plex-Token=YOUR_TOKEN"`

 **[Full Troubleshooting Guide](docs/NETWORK_CONTROL_SETUP.md#troubleshooting)**

##  Documentation

- **[Network Control Setup](docs/NETWORK_CONTROL_SETUP.md)** - Plugin installation
- **[VirtualDJ Reference](docs/VIRTUALDJ_REFERENCE.md)** - VDJScript commands
- **[MCP Production Checklist](docs/MCP_PRODUCTION_CHECKLIST.md)** - Production readiness

##  Austrian Efficiency

- **Practical solutions** over theoretical complexity
- **12 tools** instead of 62+ (81% reduction!)
- **No decision paralysis** - exactly what you need
- **Plex integration** - your music library, your way

---

**Built with Austrian efficiency for professional DJ automation! **


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.
