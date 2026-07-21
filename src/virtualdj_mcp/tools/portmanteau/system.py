"""
VDJ System Portmanteau Tool

Consolidates system status and help operations into a single interface.
Operations: status, help, connection_test
"""

import logging
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text
from rich.console import Console

from ..shared.dependencies import get_vdj_client

console = Console(file=__import__('sys').stderr)
logger = logging.getLogger(__name__)

HELP_CONTENT = {
    "overview": """
# VirtualDJ-MCP Help

## 🎯 Portmanteau Tools (13 total)

| Tool | Description |
|------|-------------|
| `vdj_deck` | Deck control (play/pause/load/seek/volume/status) |
| `vdj_mixer` | Mixing (crossfader/sync/EQ/gain/filter) |
| `vdj_library` | Library search and audio analysis |
| `vdj_automation` | Auto-DJ control and track suggestions |
| `vdj_recording` | Recording mix sessions |
| `vdj_performance` | Performance analytics and recommendations |
| `vdj_stems` | Stem separation (vocals/instrumental/drums) |
| `vdj_beatgrid` | BPM/beatgrid/loops |
| `vdj_skin` | Skin and UI control |
| `vdj_video` | Video mixing and effects |
| `vdj_plex` | Plex Media Server integration |
| `vdj_system` | System status and help |

## Quick Start

```python
# Load and play a track
vdj_deck("load", deck_id=1, track_path="C:/Music/track.mp3")
vdj_deck("play", deck_id=1)

# Search and load from Plex
vdj_plex("load_from_plex", query="ABBA", deck_id=1)

# Mix two tracks
vdj_mixer("crossfader", position=0)  # Center
vdj_mixer("sync", deck_a=1, deck_b=2)
```
""",
    "deck_control": """
# Deck Control (vdj_deck)

## Operations

- `play` - Start playback
- `pause` - Pause playback
- `toggle` - Toggle play/pause
- `stop` - Stop completely
- `load` - Load track (requires track_path)
- `seek` - Seek to position (seconds or "50%")
- `volume` - Set volume (0-100)
- `status` - Get deck status
- `load_security` - Set load security mode

## Examples

```python
vdj_deck("play", deck_id=1)
vdj_deck("load", deck_id=1, track_path="C:/Music/track.mp3")
vdj_deck("volume", deck_id=1, volume=80)
vdj_deck("seek", deck_id=1, position="50%")
vdj_deck("status", deck_id=1)
```
""",
    "mixing": """
# Mixing (vdj_mixer)

## Operations

- `crossfader` - Set crossfader (-100 to +100, 0 = center)
- `sync` - Sync BPM between decks
- `eq_high` - Set high EQ (0-100)
- `eq_mid` - Set mid EQ (0-100)
- `eq_low` - Set bass EQ (0-100)
- `gain` - Set gain (0-150)
- `filter` - Set filter (0-100)
- `master_volume` - Set master volume (0-100)
- `headphone_volume` - Set headphone cue volume (0-100)
- `headphone_mix` - Adjust cue/master mix in headphones (0-100)
- `effect` - Configure audio effects (slot, type, wet/dry, parameters)
- `eq_reset` - Reset EQ to flat 0dB

## Examples

```python
vdj_mixer("crossfader", position=-50)  # Favor deck A
vdj_mixer("sync", deck_a=1, deck_b=2)
vdj_mixer("master_volume", value=80)
vdj_mixer("effect", deck_id=1, effect_type="echo", enable=True)
```
""",
    "stems": """
# Stem Separation (vdj_stems)

VirtualDJ Stems 2.0 allows real-time isolation of:
- vocal, instru, bass, drums, hihat, kick, snare, melody

## Operations

- `kill` - Mute a stem
- `unkill` - Restore a stem
- `volume` - Set stem volume (0-100)
- `acapella` - Vocals only mode
- `instrumental` - No vocals mode
- `isolate_drums` - Drums only
- `swap` - Swap stem between decks
- `reset` - Restore all stems

## Examples

```python
vdj_stems("kill", deck_id=1, stem="vocal")     # Instant instrumental
vdj_stems("acapella", deck_id=1, enable=True)  # Vocals only
vdj_stems("swap", deck_a=1, deck_b=2, stem="vocal")  # Mashup!
```
""",
    "plex": """
# Plex Integration (vdj_plex)

Search and load tracks from Plex Media Server directly!

## Prerequisites

Set environment variables:
- `PLEX_SERVER_URL` (default: http://localhost:32400)
- `PLEX_TOKEN` (required)

## Operations

- `list_libraries` - List music libraries
- `search` - Search for tracks
- `get_path` - Get file path for a track
- `load_from_plex` - Search and load directly to deck

## Examples

```python
# List libraries
vdj_plex("list_libraries")

# Search ABBA
vdj_plex("search", query="ABBA", limit=10)

# Load directly to deck
vdj_plex("load_from_plex", query="Dancing Queen", deck_id=1)
vdj_plex("load_from_plex", artist="Pink Floyd", deck_id=2)
```
""",
}


def setup_system_portmanteau(mcp: FastMCP):
    """Register vdj_system portmanteau tool."""

    @mcp.tool()
    async def vdj_system(
        operation: Literal["status", "help", "connection_test"],
        topic: str | None = None
    ) -> Any:
        """
        System status and help for VirtualDJ-MCP.

        PORTMANTEAU PATTERN: Consolidates system tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - status: Get comprehensive system status
        - help: Get help documentation
        - connection_test: Test VirtualDJ connection

        Args:
            operation: The system operation to perform
            topic: Help topic (overview, deck_control, mixing, stems, plex)

        Returns:
            Dict with operation result

        Examples:
            vdj_system("status")
            vdj_system("help")
            vdj_system("help", topic="stems")
            vdj_system("help", topic="plex")
            vdj_system("connection_test")
        """
        try:
            if operation == "status":
                # Test VDJ connection
                connection_ok = False
                vdj_version = None

                try:
                    client = await get_vdj_client()
                    async with client:
                        result = await client.query("version")
                        if result.get("status") == "success":
                            connection_ok = True
                            vdj_version = result.get("result")
                except Exception as exc:
                    logger.debug("VirtualDJ status probe failed: %s", exc)

                vdj_status_str = f"🟢 Connected (v{vdj_version})" if connection_ok else "🔴 Disconnected"
                server_ver = "2.0.0"
                fastmcp_ver = "FastMCP 3.4.4"

                with Card(css_class="max-w-lg border border-neutral-700 bg-neutral-900 rounded-lg shadow-lg p-4") as view:
                    with CardHeader():
                        CardTitle("🖥️ VirtualDJ-MCP System Dashboard", css_class="text-lg font-bold text-white")
                    with CardContent(css_class="mt-2 space-y-2"):
                        Text("--- Server Status ---", css_class="text-sm font-semibold text-neutral-400")
                        Text("Server Name: VirtualDJ-MCP", css_class="text-sm text-neutral-300")
                        Text(f"Version: {server_ver}", css_class="text-sm text-neutral-300")
                        Text(f"Framework: {fastmcp_ver}", css_class="text-sm text-neutral-300")
                        Text("Tools Loaded: 12 Portmanteau", css_class="text-sm text-neutral-300")

                        Text("--- VirtualDJ Status ---", css_class="text-sm font-semibold text-neutral-400")
                        Text(f"Connection: {vdj_status_str}", css_class="text-sm text-neutral-300")
                        Text("API Target: HTTP Network Control Plugin", css_class="text-sm text-neutral-300")
                        Text("Host: 127.0.0.1:80", css_class="text-sm text-neutral-300")

                text_summary = f"System Status: Server: VirtualDJ-MCP v{server_ver} ({fastmcp_ver}), VirtualDJ Connection: {vdj_status_str} (Host: 127.0.0.1:80)"

                return ToolResult(
                    content=text_summary,
                    structured_content=PrefabApp(view=view, title="System Status Dashboard")
                )

            elif operation == "help":
                topic_key = topic or "overview"
                content = HELP_CONTENT.get(topic_key)

                if not content:
                    available = list(HELP_CONTENT.keys())
                    return {
                        "success": False,
                        "error": f"Unknown topic: {topic}",
                        "available_topics": available
                    }

                return {
                    "success": True,
                    "operation": "help",
                    "topic": topic_key,
                    "content": content,
                    "available_topics": list(HELP_CONTENT.keys())
                }

            elif operation == "connection_test":
                try:
                    client = await get_vdj_client()
                    async with client:
                        # Test basic query
                        result = await client.query("nop")

                        if result.get("status") == "success":
                            # Test deck query
                            deck_result = await client.query("deck 1 get_title")

                            console.print("[green]VirtualDJ connection successful![/green]")
                            return {
                                "success": True,
                                "operation": "connection_test",
                                "connected": True,
                                "message": "VirtualDJ Network Control Plugin responding",
                                "deck_1_track": deck_result.get("result", "No track loaded")
                            }
                        else:
                            return {
                                "success": False,
                                "connected": False,
                                "error": "VirtualDJ not responding"
                            }

                except Exception as e:
                    console.print(f"[red]Connection failed: {e}[/red]")
                    return {
                        "success": False,
                        "operation": "connection_test",
                        "connected": False,
                        "error": str(e),
                        "troubleshooting": [
                            "1. Ensure VirtualDJ is running",
                            "2. Install Network Control Plugin (Config → Extensions → Effects → Other)",
                            "3. Enable plugin in Master panel → Master Effect → Auto-Start",
                            "4. Check port 80 is not blocked"
                        ]
                    }

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_system: {e}[/red]")
            return {"success": False, "error": str(e)}

