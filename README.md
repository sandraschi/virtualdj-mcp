# VirtualDJ-MCP

<p align="center">
  <img src="assets/logo.png" alt="VirtualDJ-MCP Logo" width="180" style="border-radius: 50%"/>
</p>

<p align="center">
  <b>Austrian-Engineered Professional DJ Automation & Mixing Server</b>
</p>

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4.4-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

> **Installation Guide**: [INSTALL.md](INSTALL.md) — quick start, manual setup, and troubleshooting

Professional DJ automation MCP server. Provides AI-accessible control of VirtualDJ — decks, mixer, stems, video, lighting, Plex, recording, and Auto-DJ through 13 portmanteau tools (62+ operations).

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/virtualdj-mcp
cd virtualdj-mcp
just
```

Requires VirtualDJ 2023+ Pro with [Network Control Plugin](docs/NETWORK_CONTROL_SETUP.md) enabled.

---

## Tool Surface

13 portmanteau tools (set `VDJ_TOOL_MODE=individual` for 62+ legacy tools):

| Tool | Operations | Description |
|------|------------|-------------|
| `vdj_deck` | play, pause, toggle, stop, load, seek, volume, status, load_security, edit_lyrics | Deck playback control |
| `vdj_mixer` | crossfader, sync, eq_high, eq_mid, eq_low, gain, filter, master_volume, headphone_volume, headphone_mix, effect, eq_reset | Mixing and EQ |
| `vdj_library` | search, analyze | Library search and audio analysis (aubio + librosa) |
| `vdj_automation` | start, stop, status, suggest, preferences | Auto-DJ with harmonic mixing |
| `vdj_recording` | start, stop, status, list, export, delete | Mix recording |
| `vdj_performance` | metrics, stats, trends, recommendations | Performance analytics |
| `vdj_stems` | kill, unkill, volume, acapella, instrumental, isolate_drums, swap, reset, sample_stem | Real-time stem isolation (vocal, instru, bass, drums, hihat, kick, snare, melody) |
| `vdj_beatgrid` | set_bpm, tap, adjust, anchor, pitch_bend, beat_jump, loop, loop_roll, loop_exit, fluid, reanalyze_fluid | BPM, beatgrid, and loop control |
| `vdj_video` | crossfader, transition, fx, text, output, karaoke, scratch, loop, tempo_sync, load | Video mixing with effects and transitions |
| `vdj_plex` | search, get_path, load_from_plex, list_libraries | Plex Media Server integration |
| `vdj_show_control` | osc_send, os2l_button, os2l_fader, os2l_cmd | DMX lighting (OS2L → SoundSwitch/QLC+) and Resolume OSC visual sync |
| `vdj_skin` | info, load, variation, panel, panel_group, window | Skin/window management |
| `vdj_system` | status, help, connection_test | System dashboard and health |

---

## Usage Examples

```python
# Load and play
vdj_deck("load", deck_id=1, track_path="C:/Music/track.mp3")
vdj_deck("play", deck_id=1)

# Load from Plex
vdj_plex("load_from_plex", query="Dancing Queen", deck_id=1)

# Mixing
vdj_mixer("sync", deck_a=1, deck_b=2)
vdj_mixer("crossfader", position=0)

# Stem mashup
vdj_stems("swap", deck_a=1, deck_b=2, stem="vocal")

# Video
vdj_video("transition", transition_type="cube", duration=2.0)

# Recording
vdj_recording("start", name="Friday Night Mix", format="mp3")
vdj_recording("stop")
```

### Natural Language

```
"Load Dancing Queen by ABBA to deck 1 and play it"
"Search my Plex library for Pink Floyd and load to deck 2"
"Create a mashup: ABBA vocals over Pink Floyd instrumental"
```

---

## Cross-MCP Deck Handoff

Stable REST endpoints for other servers to hand off tracks without MCP coupling:

- `POST /api/v1/deck/{deck_id}/load` (`track_path`)
- `POST /api/v1/deck/{deck_id}/play_pause` (`action=play|pause|toggle`)
- `POST /api/v1/deck/{deck_id}/sync`
- `POST /api/v1/deck/{deck_id}/cue` (`mode=start|cue|set_cue`)

Used by `songgeneration-mcp` Listen exports for deck preparation before live mixing.

---

## Configuration

### Environment Variables

```env
# Network Control Plugin
VDJ_HTTP_HOST=127.0.0.1
VDJ_HTTP_PORT=80
VDJ_HTTP_PASSWORD=
VDJ_HTTP_TIMEOUT=10.0

# OSC port — must match VirtualDJ Settings > OSC
VDJ_OSC_PORT=40100

# Tool mode
VDJ_TOOL_MODE=portmanteau  # or "individual"

# Plex integration
PLEX_SERVER_URL=http://localhost:32400
PLEX_TOKEN=your_token_here

# VirtualDJ paths
VDJ_PATH=C:/Program Files/VirtualDJ/virtualdj.exe
VDJ_LIBRARY_PATH=C:/Music
```

Full reference in [.env.example](.env.example).

---

## CLI / Claude Desktop

```json
{
  "mcpServers": {
    "virtualdj-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/virtualdj-mcp", "virtualdj-mcp"],
      "env": {
        "VDJ_HTTP_HOST": "127.0.0.1",
        "VDJ_HTTP_PORT": "80"
      }
    }
  }
}
```

See [CURSOR_SETUP.md](docs/CURSOR_SETUP.md) for Cursor configuration.

---

## Requirements

- VirtualDJ 2023 or later
- VirtualDJ Pro license (for Network Control Plugin)
- Network Control Plugin enabled (Settings > Extensions > Effects > Other)
- Python 3.12+

aubio is optional (used for DJ-grade BPM detection) — lacks wheels for 3.13+. librosa fallback is functional.

---

## Architecture

```
Claude / Cursor (MCP Client)
        |
VirtualDJ-MCP Server (FastMCP 3.4.4)
  13 Portmanteau Tools
        |
VirtualDJ Client (HTTP/httpx)
        |
VirtualDJ Network Control Plugin (:80)
```

Web dashboard at port 10876, REST API at port 10877. Native Tauri 2.0 wrapper with NSIS installer available.

---

## Documentation

| Doc | Contents |
|-----|----------|
| [Installation](INSTALL.md) | All install methods |
| [Network Control Setup](docs/NETWORK_CONTROL_SETUP.md) | Plugin installation and troubleshooting |
| [VirtualDJ Reference](docs/VIRTUALDJ_REFERENCE.md) | VDJScript command reference |
| [MCP Production Checklist](docs/MCP_PRODUCTION_CHECKLIST.md) | Production readiness |
| [Cursor Setup](docs/CURSOR_SETUP.md) | Cursor IDE integration |

---

## Austrian Efficiency

- **13 tools** instead of 62+ (81% reduction)
- **No decision paralysis** — exactly what you need
- **Plex integration** — your music library, your way
- **Cross-MCP handoff** — other servers load tracks without coupling

---

**Built with Austrian efficiency for professional DJ automation.**

## SOTA Quality Stack

- **Python**: Ruff linting + formatting
- **Webapp**: Biome, TypeScript 5.9, React 19, Vite 7
- **Protocol**: Hardened stdio/stderr MCP isolation
- **Security**: Bandit + Safety audits
- **Automation**: Justfile recipes (`just lint`, `just fix`, `just build-native`, `just cua-nsis-test`)
