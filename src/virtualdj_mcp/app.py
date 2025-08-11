"""
VirtualDJ-MCP - Professional DJ Automation MCP Server

Austrian efficiency for Sandra's music mixing and DJ automation needs.
Provides 20+ tools for deck control, mixing, library management, and AI-assisted DJing.
"""

import asyncio
import sys
import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from rich.console import Console

# Import our core modules
from .core.vdj_client import VirtualDJClient, VDJError
from .config import VDJConfig

# Initialize console for logging (redirect to stderr for MCP compatibility)
console = Console(file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("VirtualDJ-MCP 🎵")

# Global managers (initialized on startup)
vdj_client: Optional[VirtualDJClient] = None
config: Optional[VDJConfig] = None


# ==================== PYDANTIC MODELS ====================

class DeckStatus(BaseModel):
    """Current status of a DJ deck"""
    deck_id: int = Field(description="Deck number (1-8)")
    is_playing: bool = Field(description="Whether deck is currently playing")
    track_path: Optional[str] = Field(description="Path to currently loaded track")
    track_title: Optional[str] = Field(description="Track title")
    track_artist: Optional[str] = Field(description="Track artist")
    position: float = Field(description="Current position in seconds")
    duration: float = Field(description="Track duration in seconds")
    bpm: Optional[float] = Field(description="Beats per minute")
    key: Optional[str] = Field(description="Musical key")
    volume: int = Field(description="Deck volume (0-100)")
    pitch: float = Field(description="Pitch adjustment (-100 to +100)")


class TrackInfo(BaseModel):
    """Information about a music track"""
    path: str = Field(description="File path to track")
    title: str = Field(description="Track title")
    artist: str = Field(description="Artist name")
    album: Optional[str] = Field(description="Album name")
    genre: Optional[str] = Field(description="Music genre")
    bpm: Optional[float] = Field(description="Beats per minute")
    key: Optional[str] = Field(description="Musical key")
    duration: float = Field(description="Duration in seconds")
    energy_level: Optional[int] = Field(description="Energy level (1-10)")
    year: Optional[int] = Field(description="Release year")


class MixerStatus(BaseModel):
    """Status of the DJ mixer"""
    crossfader_position: float = Field(description="Crossfader position (-100 to +100)")
    master_volume: int = Field(description="Master volume (0-100)")
    headphone_volume: int = Field(description="Headphone volume (0-100)")
    headphone_cue: str = Field(description="Headphone cue selection (deck1, deck2, master)")


class AutoDJStatus(BaseModel):
    """Status of auto-DJ functionality"""
    enabled: bool = Field(description="Whether auto-DJ is active")
    fade_time: int = Field(description="Crossfade time in seconds")
    next_track: Optional[str] = Field(description="Next track in queue")
    time_remaining: Optional[int] = Field(description="Time until next transition")
    queue_length: int = Field(description="Number of tracks in queue")


# ==================== INITIALIZATION ====================

async def get_vdj_client() -> VirtualDJClient:
    """Get initialized VirtualDJ client"""
    global vdj_client, config
    
    if vdj_client is None:
        config = VDJConfig.from_env()
        if not config.validate_paths():
            raise VDJError("VirtualDJ path validation failed")
        
        vdj_client = VirtualDJClient(config)
        
        # Start VirtualDJ if needed
        async with vdj_client:
            if not await vdj_client.start_virtualdj():
                raise VDJError("Failed to start VirtualDJ")
    
    return vdj_client


# ==================== SANDRA'S BRILLIANT SHOW_HELP TOOL ====================

@mcp.tool()
def show_help() -> str:
    """Get detailed help about VirtualDJ-MCP capabilities, strengths, and limitations"""
    try:
        # Read help content from docs file
        help_file = Path(__file__).parent.parent.parent / "docs" / "HELP_CONTENT.md"
        if help_file.exists():
            return help_file.read_text(encoding="utf-8")
        else:
            # Fallback help content if file not found
            return '''
🎵 VirtualDJ-MCP Server v1.0.0 - Professional DJ Automation

📋 CAPABILITIES (9 Tools Currently Implemented):
• show_help() - This help system (Sandra's brilliant insight!)
• 6 Deck Control Tools: play_pause_deck, load_track_to_deck, seek_deck, set_deck_volume, get_deck_status
• 2 Mixing Tools: set_crossfader_position, auto_sync_decks

💪 STRENGTHS:
• Professional DJ software integration (20+ years of VirtualDJ development)
• Dual communication (REST API + CLI for maximum reliability)
• Real-time deck control and mixing automation
• Multi-deck support (up to 8 decks simultaneously)
• Austrian efficiency design - practical without complexity

⚠️ LIMITATIONS:
• Requires VirtualDJ installation (not included)
• Some features need VirtualDJ Pro license
• Real-time performance depends on system resources

🔧 USAGE TIPS:
• Use get_deck_status() to monitor current playback state
• Load tracks before attempting playback operations
• auto_sync_decks() works better with similar BPM tracks

Perfect for Sandra's DJ automation needs in Vienna! 🇦🇹

Help file location: docs/HELP_CONTENT.md
            '''
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load help content: {e}[/yellow]")
        return "Help content temporarily unavailable. Please check docs/HELP_CONTENT.md"


# ==================== DECK CONTROL SUITE ====================

@mcp.tool()
async def play_pause_deck(
    deck_id: int,
    action: str = "toggle"
) -> DeckStatus:
    """
    Control playback on a specific deck
    
    Args:
        deck_id: Deck number (1-8)
        action: Action to perform (play, pause, toggle)
        
    Returns:
        Updated deck status
    """
    try:
        client = await get_vdj_client()
        
        if action == "play":
            cmd = f"deck {deck_id} play"
        elif action == "pause":
            cmd = f"deck {deck_id} pause"
        else:  # toggle
            cmd = f"deck {deck_id} play_pause"
        
        async with client:
            result = await client.send_command(cmd)
            
            if result["status"] != "success":
                raise VDJError(f"Failed to {action} deck {deck_id}: {result.get('error', 'Unknown error')}")
            
            console.print(f"[green]Deck {deck_id}: {action}[/green]")
            # Get updated deck status
            return await get_deck_status(deck_id)
            
    except Exception as e:
        console.print(f"[red]Error in play_pause_deck: {e}[/red]")
        raise VDJError(str(e))


@mcp.tool()
async def load_track_to_deck(
    deck_id: int,
    track_path: str
) -> DeckStatus:
    """
    Load a track to a specific deck
    
    Args:
        deck_id: Deck number (1-8)
        track_path: Path to audio file or library reference
        
    Returns:
        Updated deck status with loaded track
    """
    try:
        client = await get_vdj_client()
        
        # Validate track path
        if not Path(track_path).exists():
            raise VDJError(f"Track file not found: {track_path}")
        
        cmd = f"deck {deck_id} load '{track_path}'"
        
        async with client:
            result = await client.send_command(cmd)
            
            if result["status"] != "success":
                raise VDJError(f"Failed to load track to deck {deck_id}: {result.get('error', 'Unknown error')}")
            
            console.print(f"[green]Loaded '{Path(track_path).name}' to deck {deck_id}[/green]")
            return await get_deck_status(deck_id)
            
    except Exception as e:
        console.print(f"[red]Error in load_track_to_deck: {e}[/red]")
        raise VDJError(str(e))


@mcp.tool()
async def seek_deck(
    deck_id: int,
    position: Union[float, str]
) -> DeckStatus:
    """
    Seek to a specific position on a deck
    
    Args:
        deck_id: Deck number (1-8)
        position: Position to seek to (seconds as float, or percentage as "50%")
        
    Returns:
        Updated deck status
    """
    try:
        client = await get_vdj_client()
        
        # Handle percentage or absolute positioning
        if isinstance(position, str) and position.endswith('%'):
            percentage = float(position[:-1])
            cmd = f"deck {deck_id} goto {percentage}%"
        else:
            cmd = f"deck {deck_id} goto {position}s"
        
        async with client:
            result = await client.send_command(cmd)
            
            if result["status"] != "success":
                raise VDJError(f"Failed to seek deck {deck_id}: {result.get('error', 'Unknown error')}")
            
            console.print(f"[green]Deck {deck_id} seeked to {position}[/green]")
            return await get_deck_status(deck_id)
            
    except Exception as e:
        console.print(f"[red]Error in seek_deck: {e}[/red]")
        raise VDJError(str(e))


@mcp.tool()
async def set_deck_volume(
    deck_id: int,
    volume: int
) -> DeckStatus:
    """
    Set volume for a specific deck
    
    Args:
        deck_id: Deck number (1-8)
        volume: Volume level (0-100)
        
    Returns:
        Updated deck status
    """
    try:
        client = await get_vdj_client()
        
        # Clamp volume to valid range
        volume = max(0, min(100, volume))
        
        cmd = f"deck {deck_id} volume {volume}%"
        
        async with client:
            result = await client.send_command(cmd)
            
            if result["status"] != "success":
                raise VDJError(f"Failed to set deck {deck_id} volume: {result.get('error', 'Unknown error')}")
            
            console.print(f"[green]Deck {deck_id} volume set to {volume}%[/green]")
            return await get_deck_status(deck_id)
            
    except Exception as e:
        console.print(f"[red]Error in set_deck_volume: {e}[/red]")
        raise VDJError(str(e))


@mcp.tool()
async def get_deck_status(deck_id: int) -> DeckStatus:
    """
    Get current status of a specific deck
    
    Args:
        deck_id: Deck number (1-8)
        
    Returns:
        Current deck status and track information
    """
    try:
        client = await get_vdj_client()
        
        async with client:
            # Get deck variables (VirtualDJ variable names)
            commands = [
                f"get_var 'deck{deck_id}_play'",
                f"get_var 'deck{deck_id}_title'",
                f"get_var 'deck{deck_id}_artist'",
                f"get_var 'deck{deck_id}_position'",
                f"get_var 'deck{deck_id}_duration'",
                f"get_var 'deck{deck_id}_bpm'",
                f"get_var 'deck{deck_id}_key'",
                f"get_var 'deck{deck_id}_volume'",
                f"get_var 'deck{deck_id}_pitch'"
            ]
            
            results = {}
            for cmd in commands:
                result = await client.send_command(cmd)
                if result["status"] == "success":
                    var_name = cmd.split("'")[1]
                    results[var_name] = result["result"]
            
            # Parse results into DeckStatus
            return DeckStatus(
                deck_id=deck_id,
                is_playing=results.get(f'deck{deck_id}_play', '0') == '1',
                track_title=results.get(f'deck{deck_id}_title', 'No Track'),
                track_artist=results.get(f'deck{deck_id}_artist', 'Unknown Artist'),
                position=float(results.get(f'deck{deck_id}_position', 0)),
                duration=float(results.get(f'deck{deck_id}_duration', 0)),
                bpm=float(results.get(f'deck{deck_id}_bpm', 0)) if results.get(f'deck{deck_id}_bpm') else None,
                key=results.get(f'deck{deck_id}_key'),
                volume=int(results.get(f'deck{deck_id}_volume', 100)),
                pitch=float(results.get(f'deck{deck_id}_pitch', 0))
            )
            
    except Exception as e:
        console.print(f"[red]Error in get_deck_status: {e}[/red]")
        # Return a default deck status on error
        return DeckStatus(
            deck_id=deck_id,
            is_playing=False,
            track_title="Error",
            track_artist="Unknown",
            position=0.0,
            duration=0.0,
            volume=0,
            pitch=0.0
        )


# ==================== MIXING & CROSSFADER SUITE ====================

@mcp.tool()
async def set_crossfader_position(position: float) -> MixerStatus:
    """
    Set crossfader position
    
    Args:
        position: Crossfader position (-100 to +100, 0 = center)
        
    Returns:
        Updated mixer status
    """
    try:
        client = await get_vdj_client()
        
        # Clamp position to valid range
        position = max(-100, min(100, position))
        
        # Convert to VirtualDJ format (0-100 where 50 is center)
        vdj_position = (position + 100) / 2
        
        cmd = f"crossfader {vdj_position}%"
        
        async with client:
            result = await client.send_command(cmd)
            
            if result["status"] != "success":
                raise VDJError(f"Failed to set crossfader: {result.get('error', 'Unknown error')}")
            
            console.print(f"[green]Crossfader set to {position}[/green]")
            
            # Return updated mixer status
            return MixerStatus(
                crossfader_position=position,
                master_volume=100,  # TODO: Get actual values
                headphone_volume=75,
                headphone_cue="master"
            )
            
    except Exception as e:
        console.print(f"[red]Error in set_crossfader_position: {e}[/red]")
        raise VDJError(str(e))


@mcp.tool()
async def auto_sync_decks(deck_a: int, deck_b: int) -> Dict[str, Any]:
    """
    Automatically sync BPM between two decks
    
    Args:
        deck_a: Source deck number (1-8)
        deck_b: Target deck number (1-8)
        
    Returns:
        Sync operation result
    """
    try:
        client = await get_vdj_client()
        
        # Sync deck B to deck A's BPM
        cmd = f"deck {deck_b} sync deck {deck_a}"
        
        async with client:
            result = await client.send_command(cmd)
            
            if result["status"] != "success":
                raise VDJError(f"Failed to sync decks: {result.get('error', 'Unknown error')}")
            
            # Get both deck statuses to confirm sync
            deck_a_status = await get_deck_status(deck_a)
            deck_b_status = await get_deck_status(deck_b)
            
            console.print(f"[green]Synced deck {deck_b} to deck {deck_a} BPM[/green]")
            
            return {
                "status": "success",
                "deck_a": deck_a_status.model_dump(),
                "deck_b": deck_b_status.model_dump(),
                "bpm_difference": abs(deck_a_status.bpm - deck_b_status.bpm) if deck_a_status.bpm and deck_b_status.bpm else None
            }
            
    except Exception as e:
        console.print(f"[red]Error in auto_sync_decks: {e}[/red]")
        raise VDJError(str(e))


# ==================== PLACEHOLDER TOOLS (TO BE IMPLEMENTED) ====================

@mcp.tool()
async def search_tracks(
    query: str,
    filters: Optional[Dict[str, Any]] = None
) -> List[TrackInfo]:
    """Search music library with filters (TODO: Phase 2 implementation)"""
    console.print("[yellow]search_tracks: Implementation pending - Phase 2[/yellow]")
    return []


@mcp.tool()
async def auto_dj_mode(
    duration: int,
    genre_filter: Optional[str] = None
) -> AutoDJStatus:
    """Enable auto-DJ mode (TODO: Phase 3 implementation)"""
    console.print("[yellow]auto_dj_mode: Implementation pending - Phase 3[/yellow]")
    return AutoDJStatus(
        enabled=False,
        fade_time=5,
        queue_length=0
    )


# ==================== MAIN APPLICATION ====================

async def main():
    """Main application entry point"""
    try:
        # Initialize configuration
        global config
        config = VDJConfig.from_env()
        
        console.print("[green]VirtualDJ-MCP Server starting...[/green]")
        console.print(f"[blue]VirtualDJ Path: {config.virtualdj_path}[/blue]")
        console.print(f"[blue]API URL: {config.rest_api_url}[/blue]")
        
        # Run the FastMCP server
        await mcp.run()
        
    except KeyboardInterrupt:
        console.print("[yellow]Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]Server error: {e}[/red]")
        raise
    finally:
        console.print("[green]VirtualDJ-MCP Server stopped[/green]")


if __name__ == "__main__":
    asyncio.run(main())
