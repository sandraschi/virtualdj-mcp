"""
Help and Status Tools for VirtualDJ-MCP

Provides multilevel help system and system status monitoring.
"""
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from rich.console import Console

from .dependencies import get_vdj_client

# Initialize console for logging
console = Console(file=__import__('sys').stderr)


def setup_help_tools(mcp: FastMCP):
    """
    Set up help and status related MCP tools.

    Args:
        mcp: MCP instance to register tools with
    """

    @mcp.tool()
    async def show_help(level: str = "overview", category: Optional[str] = None, tool_name: Optional[str] = None) -> str:
        """
        Multilevel help system for VirtualDJ-MCP.

        Args:
            level: Help level ("overview", "categories", "detailed", "examples")
            category: Tool category for detailed help ("deck_control", "mixing", "automation", "recording", "performance", "library")
            tool_name: Specific tool name for examples and detailed usage

        Returns:
            Formatted help documentation
        """
        try:
            if level == "overview":
                return _get_overview_help()
            elif level == "categories":
                if category:
                    return _get_category_help(category)
                else:
                    return _get_categories_list()
            elif level == "detailed":
                if tool_name:
                    return _get_tool_help(tool_name)
                else:
                    return "Please specify a tool_name for detailed help"
            elif level == "examples":
                if tool_name:
                    return _get_tool_examples(tool_name)
                else:
                    return "Please specify a tool_name for examples"
            else:
                return f"Unknown help level: {level}. Use 'overview', 'categories', 'detailed', or 'examples'"

        except Exception as e:
            console.print(f"[red]Error in show_help: {e}[/red]")
            return f"Error generating help: {e}"

    @mcp.tool()
    async def get_system_status() -> Dict[str, Any]:
        """
        Get comprehensive system status for VirtualDJ-MCP server.

        Returns:
            Dict containing server status, VirtualDJ connection, performance metrics
        """
        try:
            status = get_system_status()

            # Get VDJ connection status
            try:
                vdj_client = await get_vdj_client()
                vdj_status = await vdj_client.is_running()
                status["vdj_connected"] = vdj_status

                if vdj_status:
                    vdj_details = await vdj_client.get_status()
                    status["vdj_details"] = vdj_details
            except Exception as e:
                status["vdj_connected"] = False
                status["vdj_error"] = str(e)

            # Calculate uptime
            if "start_time" in status and status["start_time"]:
                status["uptime_seconds"] = int(time.time() - status["start_time"])

            # Add timestamp
            status["timestamp"] = datetime.now().isoformat()

            return status

        except Exception as e:
            console.print(f"[red]Error getting system status: {e}[/red]")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def _get_overview_help() -> str:
    """Get overview help text"""
    return """
🎵 **VirtualDJ-MCP Server v1.2.0** - Professional DJ Automation

**Multilevel Help System:**
• `show_help()` - This overview
• `show_help(level="categories")` - List all tool categories
• `show_help(level="categories", category="deck_control")` - Category details
• `show_help(level="detailed", tool_name="play_pause_deck")` - Tool specifics
• `show_help(level="examples", tool_name="load_track_to_deck")` - Usage examples

**System Status:**
• `get_system_status()` - Server health, VDJ connection, performance metrics

**Core Capabilities:**
• **25+ Professional Tools** across 6 categories
• **Real VirtualDJ Integration** via CLI commands and VDJScript
• **Production-Ready** with comprehensive error handling
• **AI-Powered Recommendations** for DJ performance improvement

**Getting Started:**
1. Ensure VirtualDJ is installed and accessible
2. Use `show_help(level="categories")` to explore tool categories
3. Try examples with `show_help(level="examples", tool_name="...")`

**Need Help?** Use the multilevel help system or check the documentation!
"""


def _get_categories_list() -> str:
    """Get list of available tool categories"""
    return """
🔧 **VirtualDJ-MCP Tool Categories**

**1. 🎛️ Deck Control**
   Basic deck operations: playback, loading, volume, seeking
   • `play_pause_deck()` - Control deck playback
   • `load_track_to_deck()` - Load tracks to decks
   • `set_deck_volume()` - Adjust deck volume
   • `get_deck_status()` - Get deck information

**2. 🎚️ Mixing Tools**
   Crossfader, EQ, synchronization, effects
   • `set_crossfader_position()` - Move crossfader
   • `auto_sync_decks()` - BPM synchronization
   • `set_eq_band()` - Control EQ bands
   • `set_effect()` - Apply audio effects

**3. 🤖 Automation**
   Auto-DJ, intelligent track selection, recording
   • `auto_dj_mode()` - Start automated mixing
   • `suggest_next_track()` - AI track recommendations
   • `start_recording()` - Record DJ mixes
   • `get_auto_dj_status()` - Auto-DJ monitoring

**4. 📊 Performance Monitoring**
   Real-time analytics, recommendations, reporting
   • `get_current_metrics()` - Live performance data
   • `get_recommendations()` - AI-powered improvement tips
   • `analyze_trends()` - Historical trend analysis
   • `export_data()` - Export performance reports

**5. 🎵 Library Management**
   Track browsing, searching, information
   • `browse_library()` - Navigate music library
   • `search_tracks()` - Find tracks by criteria
   • `get_track_info()` - Detailed track metadata

**6. 🔧 System Tools**
   Help, status, configuration
   • `show_help()` - Multilevel help system
   • `get_system_status()` - Server and VDJ status

**Usage:** `show_help(level="categories", category="deck_control")` for category details
"""


def _get_category_help(category: str) -> str:
    """Get detailed help for a specific category"""
    category_helps = {
        "deck_control": """
🎛️ **Deck Control Tools**

**Core Functions:**
• `play_pause_deck(deck_id: int, action: str)` - Control playback
  - deck_id: 1-8 (deck number)
  - action: "play", "pause", "toggle"

• `load_track_to_deck(deck_id: int, track_path: str)` - Load audio files
  - Supports MP3, WAV, FLAC, AIFF formats
  - Use absolute paths for reliability

• `seek_deck(deck_id: int, position: float)` - Jump to position
  - position: 0.0-1.0 (percentage) or seconds

• `set_deck_volume(deck_id: int, volume: int)` - Volume control
  - volume: 0-100 (percentage)

• `get_deck_status(deck_id: int)` - Current deck information
  - Returns track title, artist, BPM, position, volume

**Examples:**
• Load track: `load_track_to_deck(1, "C:/Music/track.mp3")`
• Start playing: `play_pause_deck(1, "play")`
• Check status: `get_deck_status(1)`
""",

        "mixing": """
🎚️ **Mixing Tools**

**Crossfader Control:**
• `set_crossfader_position(position: int)` - Move crossfader
  - position: -100 (full left) to +100 (full right)

**BPM Synchronization:**
• `auto_sync_decks(deck_a: int, deck_b: int)` - Sync deck BPMs
  - Automatically matches tempo between decks

**EQ Control:**
• `set_eq_band(deck_id: int, band: str, value: int, kill: bool)` - EQ adjustments
  - band: "high", "mid", "low"
  - value: -20 to +20 dB (or use kill=True for -∞dB)

**Audio Effects:**
• `set_effect(deck_id: int, effect_slot: int, effect_type: str, enabled: bool, wet_dry: float, param1: float, param2: float)` - Apply effects
  - Supports VirtualDJ's built-in effects

**Examples:**
• Center crossfader: `set_crossfader_position(0)`
• Sync decks: `auto_sync_decks(1, 2)`
• Kill bass: `set_eq_band(1, "low", 0, True)`
""",

        "automation": """
🤖 **Automation Tools**

**Auto-DJ System:**
• `auto_dj_mode(duration_minutes: int, genre_filter: str, bpm_range: tuple, energy_level: str)` - Start automated mixing
• `stop_auto_dj()` - Stop automated mixing
• `get_auto_dj_status()` - Monitor Auto-DJ progress

**Intelligent Track Selection:**
• `suggest_next_track(style: str, current_track_id: str, limit: int)` - AI-powered recommendations
• `set_auto_dj_preferences(fade_time: float, energy_matching: bool, harmonic_mixing: bool)` - Configure preferences

**Recording:**
• `start_recording(name: str, format: str)` - Start mix recording
• `stop_recording()` - Stop recording
• `get_recording_status()` - Monitor recording progress

**Examples:**
• Start Auto-DJ: `auto_dj_mode(30, "Techno", (128, 135), "high")`
• Get suggestions: `suggest_next_track("House", "track123", 5)`
• Start recording: `start_recording("MyMix", "mp3")`
""",

        "performance": """
📊 **Performance Monitoring Tools**

**Real-Time Metrics:**
• `get_current_metrics()` - Live DJ performance data
  - BPM stability, beat match quality, energy flow
  - Current track analysis, transition quality

**AI Recommendations:**
• `get_recommendations()` - Intelligent improvement suggestions
  - BPM stabilization tips, energy flow advice
  - Transition improvement recommendations

**Trend Analysis:**
• `analyze_trends(hours: int, metric: str)` - Historical performance analysis
  - BPM trends, energy progression patterns
  - Performance improvement over time

**Data Export:**
• `export_data(format: str, filename: str)` - Export performance data
  - JSON format for analysis and reporting

**Examples:**
• Check performance: `get_current_metrics()`
• Get advice: `get_recommendations()`
• Analyze trends: `analyze_trends(24, "bpm")`
""",

        "library": """
🎵 **Library Management Tools**

**Library Navigation:**
• `browse_library(path: str, filter_type: str)` - Browse music folders
• `get_track_info(track_id: str)` - Detailed track metadata

**Search & Discovery:**
• `search_tracks(query: str, filters: dict)` - Find tracks
  - Search by artist, title, genre, BPM range
  - Filter by energy level, key compatibility

**Examples:**
• Browse folder: `browse_library("C:/Music", "folder")`
• Search tracks: `search_tracks("Techno", {"bpm_min": 128, "bpm_max": 135})`
• Get info: `get_track_info("track123")`
""",

        "system": """
🔧 **System Tools**

**Help System:**
• `show_help(level: str, category: str, tool_name: str)` - Multilevel help
  - Overview, categories, detailed tool info, examples

**System Status:**
• `get_system_status()` - Server and VirtualDJ status
  - Connection status, uptime, performance metrics
  - VirtualDJ connectivity and health checks

**Examples:**
• Get help: `show_help("categories", "deck_control")`
• System status: `get_system_status()`
"""
    }

    return category_helps.get(category, f"Unknown category: {category}")


def _get_tool_help(tool_name: str) -> str:
    """Get detailed help for a specific tool"""
    tool_helps = {
        "play_pause_deck": """
🎵 **play_pause_deck(deck_id: int, action: str) -> DeckStatus**

Control playback on a specific deck.

**Parameters:**
• `deck_id`: Deck number (1-8)
• `action`: "play", "pause", or "toggle"

**Returns:**
• `DeckStatus` object with updated deck information

**Examples:**
• `play_pause_deck(1, "play")` - Start deck 1
• `play_pause_deck(2, "pause")` - Pause deck 2
• `play_pause_deck(1, "toggle")` - Toggle deck 1 playback
""",

        "load_track_to_deck": """
🎵 **load_track_to_deck(deck_id: int, track_path: str) -> DeckStatus**

Load an audio track to a specific deck.

**Parameters:**
• `deck_id`: Deck number (1-8)
• `track_path`: Absolute path to audio file (MP3, WAV, FLAC, AIFF)

**Returns:**
• `DeckStatus` object with loaded track information

**Examples:**
• `load_track_to_deck(1, "C:/Music/techno/track.mp3")`
• `load_track_to_deck(2, "C:/Users/name/Music/house/song.wav")`
""",

        "get_recommendations": """
📊 **get_recommendations() -> Dict[str, Any]**

Get AI-powered recommendations for improving DJ performance.

**Returns:**
• Dictionary with recommendation categories:
  - `bpm_adjustments`: BPM stability suggestions
  - `energy_suggestions`: Energy flow tips
  - `transition_tips`: Mixing improvement advice
  - `crowd_engagement`: Audience response suggestions

**Example:**
```python
result = get_recommendations()
# Returns actionable DJ improvement tips
```
"""
    }

    return tool_helps.get(tool_name, f"Detailed help for '{tool_name}' not available yet.")


def _get_tool_examples(tool_name: str) -> str:
    """Get usage examples for a specific tool"""
    examples = {
        "play_pause_deck": """
🎵 **play_pause_deck Examples:**

**Basic Playback Control:**
```python
# Start deck 1
result = await play_pause_deck(1, "play")

# Pause deck 2
result = await play_pause_deck(2, "pause")

# Toggle deck 1 (play if paused, pause if playing)
result = await play_pause_deck(1, "toggle")
```

**Workflow Example:**
```python
# Load and start playback
await load_track_to_deck(1, "C:/Music/track1.mp3")
await play_pause_deck(1, "play")

# Start second track
await load_track_to_deck(2, "C:/Music/track2.mp3")
await play_pause_deck(2, "play")
```
""",

        "load_track_to_deck": """
🎵 **load_track_to_deck Examples:**

**Loading Different Audio Formats:**
```python
# MP3 file
await load_track_to_deck(1, "C:/Music/techno/beat.mp3")

# WAV file
await load_track_to_deck(2, "C:/Music/house/track.wav")

# FLAC file
await load_track_to_deck(1, "C:/Music/dnb/bassline.flac")
```

**Complete Loading Workflow:**
```python
# Load track and check status
result = await load_track_to_deck(1, "C:/Music/song.mp3")
print(f"Loaded: {result.track.title} by {result.track.artist}")

# Verify load was successful
status = await get_deck_status(1)
if status.track.title:
    print("Track loaded successfully!")
```
""",

        "get_recommendations": """
📊 **get_recommendations Examples:**

**Getting Performance Advice:**
```python
# Get current recommendations
advice = await get_recommendations()

# Check for BPM issues
if advice['bpm_adjustments']:
    print("BPM Issues Found:")
    for tip in advice['bpm_adjustments']:
        print(f"• {tip['message']}")

# Check energy flow
if advice['energy_suggestions']:
    print("Energy Tips:")
    for tip in advice['energy_suggestions']:
        print(f"• {tip['message']}")
```

**Typical Output:**
```json
{
  "bpm_adjustments": [{
    "type": "bpm_stabilization",
    "message": "BPM stability is low (65%). Consider using VirtualDJ's beat grid.",
    "severity": "high"
  }],
  "transition_tips": [{
    "type": "bpm_transition",
    "message": "Large BPM change detected (8 BPM). Use pitch bend for smoother mix.",
    "severity": "high"
  }]
}
```
"""
    }

    return examples.get(tool_name, f"Examples for '{tool_name}' not available yet.")



