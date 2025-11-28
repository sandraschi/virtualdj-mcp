# VirtualDJ Network Control Plugin Setup

VirtualDJ-MCP uses VirtualDJ's **Network Control Plugin** for HTTP-based communication. This replaces the legacy CLI approach and provides reliable, real-time control of VirtualDJ.

## Requirements

- **VirtualDJ 2023 or later**
- **VirtualDJ Pro license** (required for the Network Control Plugin)
- Python 3.11+
- `httpx` library (included in requirements.txt)

## Plugin Installation

### Step 1: Install the Network Control Plugin

1. Open **VirtualDJ**
2. Go to **Config** → **Extensions**
3. Navigate to **Effects** → **Other**
4. Find and install **"Network Control"**

![Network Control Plugin Location](https://www.virtualdj.com/wiki/networkcontrolplugin)

### Step 2: Configure the Plugin

1. After installation, go to the **Master panel**
2. Click the **Master Effect** dropdown
3. Look in the **Auto-Start** category
4. Find **Network Control** and click the **⚙️ cog wheel** to open settings

### Step 3: Plugin Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **IP Port** | 80 | HTTP port for API access |
| **Authentication** | (empty) | Optional password for security |

**Recommended settings:**
- Port: `80` (or `8080` if port 80 is in use)
- Authentication: Set a password if on a shared network

### Step 4: Enable Auto-Start (Optional)

To have the plugin start automatically with VirtualDJ:
1. In the Master Effect dropdown, right-click on Network Control
2. Select "Auto-start on VirtualDJ launch"

## VirtualDJ-MCP Configuration

### Environment Variables

```env
# Network Control Plugin settings
VDJ_HTTP_HOST=127.0.0.1
VDJ_HTTP_PORT=80
VDJ_HTTP_PASSWORD=your_password_here  # Optional
VDJ_HTTP_TIMEOUT=10.0

# VirtualDJ path (for process detection)
VDJ_PATH=C:/Program Files/VirtualDJ/virtualdj.exe
```

### Claude Desktop / Cursor MCP Config

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "python",
      "args": ["-m", "virtualdj_mcp.server"],
      "cwd": "D:/Dev/repos/virtualdj-mcp",
      "env": {
        "PYTHONPATH": "D:/Dev/repos/virtualdj-mcp/src",
        "PYTHONUNBUFFERED": "1",
        "VDJ_HTTP_PORT": "80"
      }
    }
  }
}
```

## HTTP API Reference

The Network Control Plugin exposes two endpoints:

### Execute Commands

**POST** `/execute`
- Executes VDJScript commands
- Returns `true` or `false`

```bash
# Play deck 1
curl -X POST http://127.0.0.1:80/execute \
  -H "Content-Type: text/plain" \
  -d "deck 1 play"

# Load a track
curl -X POST http://127.0.0.1:80/execute \
  -H "Content-Type: text/plain" \
  -d "deck 1 load 'E:/Music/track.mp3'"
```

### Query Information

**POST** `/query`
- Queries VirtualDJ for information
- Returns the result value

```bash
# Get deck 1 title
curl -X POST http://127.0.0.1:80/query \
  -H "Content-Type: text/plain" \
  -d "deck 1 get_title"

# Get BPM
curl -X POST http://127.0.0.1:80/query \
  -H "Content-Type: text/plain" \
  -d "deck 1 get_bpm"
```

### Authentication

If you set a password in the plugin settings:

```bash
# Via header
curl -X POST http://127.0.0.1:80/execute \
  -H "Authorization: Bearer mypassword" \
  -H "Content-Type: text/plain" \
  -d "deck 1 play"

# Via URL parameter
curl -X POST "http://127.0.0.1:80/execute?bearer=mypassword" \
  -H "Content-Type: text/plain" \
  -d "deck 1 play"
```

## Common VDJScript Commands

### Deck Control
| Command | Description |
|---------|-------------|
| `deck N play` | Start playback |
| `deck N pause` | Pause playback |
| `deck N stop` | Stop playback |
| `deck N play_pause` | Toggle play/pause |
| `deck N load 'path'` | Load track from path |

### Deck Queries
| Query | Returns |
|-------|---------|
| `deck N get_title` | Track title |
| `deck N get_artist` | Track artist |
| `deck N get_bpm` | BPM value |
| `deck N get_key` | Musical key |
| `deck N get_position` | Current position (ms) |
| `deck N get_songlength` | Track duration (ms) |
| `deck N get_isplaying` | 1 if playing, 0 if not |
| `deck N get_filepath` | Full file path |

### Mixer Control
| Command | Description |
|---------|-------------|
| `crossfader N%` | Set crossfader (0-100) |
| `deck N volume N%` | Set deck volume (0-100) |
| `master_volume N%` | Set master volume |

### Auto-DJ
| Command | Description |
|---------|-------------|
| `automix on` | Enable Auto-DJ |
| `automix off` | Disable Auto-DJ |

## Troubleshooting

### Plugin Not Responding

1. **Check VirtualDJ is running** - The plugin only works when VirtualDJ is open
2. **Verify plugin is enabled** - Check Master Effect dropdown shows Network Control active
3. **Check port availability** - Ensure port 80 isn't blocked by firewall or another service

```powershell
# Test if plugin is responding
Invoke-WebRequest -Uri "http://127.0.0.1:80/execute" -Method POST -Body "nop" -ContentType "text/plain"
```

### Connection Refused

- VirtualDJ not running
- Network Control Plugin not enabled
- Wrong port configured
- Firewall blocking connection

### Authentication Errors (HTTP 401)

- Password mismatch between plugin settings and MCP config
- Check `VDJ_HTTP_PASSWORD` environment variable

### Commands Return "false"

- Invalid VDJScript syntax
- Deck number out of range (1-8)
- File path doesn't exist (for load commands)
- VirtualDJ internal error

## Architecture

```
┌─────────────────┐     HTTP POST      ┌──────────────────────┐
│                 │ ─────────────────► │                      │
│  VirtualDJ-MCP  │                    │  Network Control     │
│    (Python)     │ ◄───────────────── │  Plugin (VirtualDJ)  │
│                 │     Response       │                      │
└─────────────────┘                    └──────────────────────┘
        │                                        │
        │                                        │
        ▼                                        ▼
┌─────────────────┐                    ┌──────────────────────┐
│  Claude/Cursor  │                    │    VirtualDJ Core    │
│   MCP Client    │                    │   (Decks, Mixer,     │
│                 │                    │    Library, etc.)    │
└─────────────────┘                    └──────────────────────┘
```

## Migration from CLI (Legacy)

The old CLI approach (`virtualdj.exe -cmd "command"`) is deprecated. Benefits of HTTP:

| Feature | CLI (Legacy) | HTTP (Current) |
|---------|--------------|----------------|
| Control running instance | ❌ Limited | ✅ Full |
| Query deck status | ❌ No | ✅ Yes |
| Real-time feedback | ❌ No | ✅ Yes |
| Complex commands | ❌ Escaping issues | ✅ Works |
| Performance | ❌ Process spawn overhead | ✅ Fast HTTP |

## Further Reading

- [VirtualDJ Network Control Plugin Wiki](https://www.virtualdj.com/wiki/networkcontrolplugin)
- [VDJScript Reference](https://www.virtualdj.com/wiki/vdjscript.html)
- [VDJScript Verbs](https://www.virtualdj.com/manuals/virtualdj/appendix/vdjscriptverbs/)

