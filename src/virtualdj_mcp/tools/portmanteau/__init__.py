"""
VirtualDJ-MCP Portmanteau Tools

Consolidates 62+ individual tools into 13 unified portmanteau interfaces.
This follows the FastMCP 2.13+ best practices for feature-rich MCP servers.

PORTMANTEAU TOOLS (13 total):
1. vdj_deck - Deck control (play/pause/load/seek/volume/status)
2. vdj_mixer - Mixing operations (crossfader/sync)
3. vdj_library - Library management (search/analyze)
4. vdj_automation - Auto-DJ control
5. vdj_recording - Recording operations
6. vdj_performance - Performance analytics
7. vdj_stems - Stem separation
8. vdj_beatgrid - BPM/loops/beatgrid
9. vdj_skin - Skin control
10. vdj_video - Video operations
11. vdj_plex - Plex integration (NEW)
12. vdj_help - Help system
13. vdj_system - System status

BENEFITS:
- 62+ tools → 13 tools (79% reduction)
- Better UX with grouped operations
- Easier discovery by category
- AI-friendly comprehensive docstrings
"""

from .automation import setup_automation_portmanteau
from .beatgrid import setup_beatgrid_portmanteau
from .deck import setup_deck_portmanteau
from .library import setup_library_portmanteau
from .mixer import setup_mixer_portmanteau
from .performance import setup_performance_portmanteau
from .plex import setup_plex_portmanteau
from .recording import setup_recording_portmanteau
from .skin import setup_skin_portmanteau
from .show_control import setup_show_control_portmanteau
from .stems import setup_stems_portmanteau
from .system import setup_system_portmanteau
from .video import setup_video_portmanteau


def setup_all_portmanteau_tools(mcp):
    """Register all portmanteau tools with the MCP server."""
    setup_deck_portmanteau(mcp)
    setup_mixer_portmanteau(mcp)
    setup_library_portmanteau(mcp)
    setup_automation_portmanteau(mcp)
    setup_recording_portmanteau(mcp)
    setup_performance_portmanteau(mcp)
    setup_stems_portmanteau(mcp)
    setup_beatgrid_portmanteau(mcp)
    setup_skin_portmanteau(mcp)
    setup_video_portmanteau(mcp)
    setup_plex_portmanteau(mcp)
    setup_show_control_portmanteau(mcp)
    setup_system_portmanteau(mcp)


__all__ = [
    "setup_all_portmanteau_tools",
    "setup_automation_portmanteau",
    "setup_beatgrid_portmanteau",
    "setup_deck_portmanteau",
    "setup_library_portmanteau",
    "setup_mixer_portmanteau",
    "setup_performance_portmanteau",
    "setup_plex_portmanteau",
    "setup_recording_portmanteau",
    "setup_skin_portmanteau",
    "setup_show_control_portmanteau",
    "setup_stems_portmanteau",
    "setup_system_portmanteau",
    "setup_video_portmanteau",
]

