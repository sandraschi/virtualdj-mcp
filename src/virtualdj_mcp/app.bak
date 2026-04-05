"""
VirtualDJ-MCP - Professional DJ Automation MCP Server

Austrian efficiency for Sandra's music mixing and DJ automation needs.
Provides 20+ tools for deck control, mixing, library management, and AI-assisted DJing.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .config import VDJConfig

# Import our core modules
from .core.vdj_client import VDJError, VirtualDJClient
from .services.audio_analysis import AudioAnalyzer
from .services.automation_engine import AutomationEngine

# Import services
from .services.library_scanner import LibraryScanner
from .services.library_scanner import TrackInfo as ScannerTrackInfo
from .services.playlist_manager import PlaylistManager
from .services.recording_service import RecordingService

# Initialize console and logger for logging (redirect to stderr for MCP compatibility)
import logging
console = Console(file=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("VirtualDJ-MCP ")
mcp = FastMCP("VirtualDJ-MCP 🎵")

# Global managers (initialized on startup)
vdj_client: Optional[VirtualDJClient] = None
config: Optional[VDJConfig] = None
automation_engine: Optional[AutomationEngine] = None
recording_service: Optional[RecordingService] = None
library_scanner: Optional[LibraryScanner] = None
audio_analyzer: Optional[AudioAnalyzer] = None
playlist_manager: Optional[PlaylistManager] = None


# Service getter functions
async def get_library_scanner() -> LibraryScanner:
    """Get or create library scanner instance"""
    global library_scanner
    if library_scanner is None:
        library_scanner = LibraryScanner()
    return library_scanner


async def get_audio_analyzer() -> AudioAnalyzer:
    """Get or create audio analyzer instance"""
    global audio_analyzer
    if audio_analyzer is None:
        audio_analyzer = AudioAnalyzer()
    return audio_analyzer


async def get_playlist_manager() -> PlaylistManager:
    """Get or create playlist manager instance"""
    global playlist_manager
    if playlist_manager is None:
        playlist_manager = PlaylistManager()
    return playlist_manager


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
    """Information about a music track with extended metadata"""
    path: str = Field(..., description="File path to track")
    title: str = Field(..., description="Track title")
    artist: str = Field(..., description="Artist name")
    album: Optional[str] = Field(None, description="Album name")
    genre: Optional[str] = Field(None, description="Music genre")
    bpm: Optional[float] = Field(None, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key")
    duration: float = Field(0.0, description="Duration in seconds")
    energy: Optional[float] = Field(None, description="Energy level (0.0-1.0)")
    danceability: Optional[float] = Field(None, description="Danceability score (0.0-1.0)")
    year: Optional[int] = Field(None, description="Release year")
    bitrate: Optional[int] = Field(None, description="Audio bitrate (kbps)")
    sample_rate: Optional[int] = Field(None, description="Sample rate (Hz)")
    channels: Optional[int] = Field(None, description="Number of audio channels")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    last_modified: Optional[float] = Field(None, description="Last modified timestamp")
    play_count: int = Field(0, description="Number of times played")
    rating: int = Field(0, description="User rating (0-5)")
    tags: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }
    
    @classmethod
    def from_scanner_track(cls, track: ScannerTrackInfo) -> 'TrackInfo':
        """Create from LibraryScanner's TrackInfo"""
        return cls(
            path=track.file_path,
            title=track.title or Path(track.file_path).stem,
            artist=track.artist or "Unknown Artist",
            album=track.album,
            genre=track.genre,
            bpm=track.bpm,
            key=track.key,
            duration=track.duration,
            year=track.year,
            bitrate=track.bitrate,
            sample_rate=track.sample_rate,
            channels=track.channels,
            file_size=track.file_size,
            last_modified=track.last_modified,
            play_count=track.play_count,
            rating=track.rating,
            tags=track.tags
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        return json.loads(self.json())


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
async def show_help() -> str:
    """
    Get detailed help about VirtualDJ-MCP capabilities, tools, and usage.
    
    Returns:
        str: Formatted help documentation
    """
    try:
        # Read help content from docs file if it exists
        help_file = Path(__file__).parent.parent.parent / "docs" / "HELP_CONTENT.md"
        if help_file.exists():
            return help_file.read_text(encoding="utf-8")
            
        # Fallback help content
        help_text = """
🎵 VirtualDJ-MCP Server v1.2.0 - Professional DJ Automation

📋 TOOL CATEGORIES:

1. [sync] DECK CONTROL:
   • play_pause_deck(deck_id, action) - Control deck playback
   • load_track_to_deck(deck_id, track_path) - Load track to deck
   • seek_deck(deck_id, position) - Seek to position
   • set_deck_volume(deck_id, volume) - Set deck volume (0-100)
   • get_deck_status(deck_id) - Get deck status and track info

2. [fader]️ MIXING TOOLS:
   • set_crossfader_position(position) - Set crossfader (-100 to 100)
   • auto_sync_decks(deck_a, deck_b) - Sync BPM between decks
   • set_eq_band(deck_id, band, value, kill) - Control EQ bands
   • set_effect(deck_id, effect_slot, effect_type, enabled, wet_dry, param1, param2) - Apply effects

3. 🤖 AUTO-DJ TOOLS:
   • auto_dj_mode(duration_minutes, genre_filter, ...) - Start Auto-DJ
   • stop_auto_dj() - Stop Auto-DJ
   • get_auto_dj_status() - Get Auto-DJ status
   • suggest_next_track(style, current_track_id, limit) - Get track suggestions
   • set_auto_dj_preferences(fade_time, energy_matching, ...) - Configure Auto-DJ

4. [record]️ RECORDING TOOLS:
   • start_recording(name, format) - Start recording mix
   • stop_recording() - Stop recording
   • get_recording_status(recording_id) - Get recording status
   • list_recordings(limit, offset) - List available recordings
   • export_mix_history(format, include_tracklist) - Export mix history
   • delete_recording(recording_id) - Delete a recording

5. ℹ️ SYSTEM TOOLS:
   • show_help() - This help system
   • search_tracks(query, filters) - Search music library
   • analyze_track_audio(track_path) - Analyze track audio features

💡 USAGE TIPS:
• Use get_deck_status() to monitor playback state
• Auto-DJ works best with a well-organized music library
• Recordings are saved in the configured recordings directory
• Check the README for detailed parameter documentation

[search] For detailed documentation, visit the project's GitHub repository.

Perfect for Sandra's professional DJ automation needs in Vienna! 
"""
        return help_text.strip()
        
    except Exception as e:
        logger.error(f"Error generating help content: {e}", exc_info=True)
        return f"Error generating help content: {str(e)}"
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
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def search_tracks(
    query: str = "",
    limit: int = 50,
    artist: Optional[str] = None,
    genre: Optional[str] = None,
    bpm_min: Optional[float] = None,
    bpm_max: Optional[float] = None,
    key: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    duration_min: Optional[float] = None,
    duration_max: Optional[float] = None,
    energy_min: Optional[float] = None,
    energy_max: Optional[float] = None,
    sort_by: str = "relevance",
    sort_desc: bool = True
) -> List[Dict[str, Any]]:
    """
    Search the music library with advanced filtering and sorting.
    
    Args:
        query: Text search query (searches in title, artist, album, and tags)
        limit: Maximum number of results to return (1-1000)
        artist: Filter by artist name (partial match, case-insensitive)
        genre: Filter by genre (partial match, case-insensitive)
        bpm_min: Minimum BPM (beats per minute)
        bpm_max: Maximum BPM (beats per minute)
        key: Filter by musical key (e.g., 'C', 'A#m')
        year_min: Minimum release year
        year_max: Maximum release year
        duration_min: Minimum duration in seconds
        duration_max: Maximum duration in seconds
        energy_min: Minimum energy level (0.0-1.0)
        energy_max: Maximum energy level (0.0-1.0)
        sort_by: Field to sort by (relevance, title, artist, bpm, year, duration, energy)
        sort_desc: Sort in descending order (True) or ascending (False)
        
    Returns:
        List of matching tracks with metadata
    """
    # Validate inputs
    limit = max(1, min(1000, limit))  # Clamp limit to 1-1000
    
    # Get scanner instance
    scanner = await get_library_scanner()
    
    # Scan library if needed (in a real app, you'd have a pre-scanned database)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("Searching library...", total=None)
        
        try:
            # In a real implementation, you'd query a database here
            # For now, we'll scan the directory on each search (not recommended for production)
            tracks = await scanner.scan_directory(recursive=True)
            
            # Convert to TrackInfo objects
            track_infos = [TrackInfo.from_scanner_track(track) for track in tracks]
            
            # Apply filters
            filtered_tracks = []
            for track in track_infos:
                # Skip if any filter doesn't match
                if query and query.lower() not in (track.title + " " + track.artist).lower():
                    continue
                if artist and artist.lower() not in (track.artist or "").lower():
                    continue
                if genre and genre.lower() not in (track.genre or "").lower():
                    continue
                if bpm_min is not None and (track.bpm is None or track.bpm < bpm_min):
                    continue
                if bpm_max is not None and (track.bpm is None or track.bpm > bpm_max):
                    continue
                if key and track.key and key.upper() != track.key.upper():
                    continue
                if year_min is not None and (track.year is None or track.year < year_min):
                    continue
                if year_max is not None and (track.year is None or track.year > year_max):
                    continue
                if duration_min is not None and track.duration < duration_min:
                    continue
                if duration_max is not None and track.duration > duration_max:
                    continue
                if energy_min is not None and (track.energy is None or track.energy < energy_min):
                    continue
                if energy_max is not None and (track.energy is None or track.energy > energy_max):
                    continue
                
                filtered_tracks.append(track)
            
            # Sort results
            if sort_by == "relevance" and query:
                # Simple relevance sort based on query matches
                def relevance_score(track: TrackInfo) -> int:
                    score = 0
                    if query.lower() in (track.title or "").lower():
                        score += 3
                    if query.lower() in (track.artist or "").lower():
                        score += 2
                    if query.lower() in (track.album or "").lower():
                        score += 1
                    return score
                
                filtered_tracks.sort(key=relevance_score, reverse=not sort_desc)
            elif sort_by == "title":
                filtered_tracks.sort(key=lambda x: (x.title or "").lower(), reverse=sort_desc)
            elif sort_by == "artist":
                filtered_tracks.sort(key=lambda x: (x.artist or "").lower(), reverse=sort_desc)
            elif sort_by == "bpm":
                filtered_tracks.sort(key=lambda x: x.bpm or 0, reverse=sort_desc)
            elif sort_by == "year":
                filtered_tracks.sort(key=lambda x: x.year or 0, reverse=sort_desc)
            elif sort_by == "duration":
                filtered_tracks.sort(key=lambda x: x.duration or 0, reverse=sort_desc)
            elif sort_by == "energy":
                filtered_tracks.sort(key=lambda x: x.energy or 0, reverse=sort_desc)
            
            # Apply limit
            result_tracks = filtered_tracks[:limit]
            
            # Convert to dictionaries for JSON serialization
            return [track.to_dict() for track in result_tracks]
            
        except Exception as e:
            console.print(f"[red]Error during search: {str(e)}[/red]")
            return []
        finally:
            progress.update(task, completed=1, visible=False)

@mcp.tool()
async def analyze_track_audio(track_path: str) -> Dict[str, Any]:
    """
    Analyze an audio file to extract BPM, key, and other audio features.
    
    Args:
        track_path: Path to the audio file to analyze
        
    Returns:
        Dictionary containing audio analysis results
    """
    try:
        analyzer = await get_audio_analyzer()
        features = await analyzer.analyze_file(track_path)
        
        # Convert to a serializable format
        result = {
            "bpm": features.bpm,
            "key": str(features.key) if features.key else None,
            "energy": features.energy,
            "danceability": features.danceability,
            "loudness": features.loudness,
            "spectral_centroid": features.spectral_centroid,
            "zero_crossing_rate": features.zero_crossing_rate,
            "onset_strength": features.onset_strength,
            "beats": features.beats[:100],  # Limit number of beats to return
            "analysis_successful": True
        }
        
        return result
        
    except Exception as e:
        console.print(f"[red]Error analyzing audio: {str(e)}[/red]")
        return {
            "analysis_successful": False,
            "error": str(e)
        }

@mcp.tool()
async def auto_dj_mode(
    duration: int,
    genre_filter: Optional[str] = None,
    target_bpm: Optional[float] = None,
    energy_level: Optional[str] = None,
    mood: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enable auto-DJ mode to automatically mix tracks based on criteria.
    
    Args:
        duration: Duration in minutes for the auto-DJ session
        genre_filter: Optional genre to filter tracks
        target_bpm: Target BPM for the mix (None for auto-detect)
        energy_level: Desired energy level (low, medium, high, peak)
        mood: Desired mood (chill, upbeat, intense, etc.)
        
    Returns:
        Dictionary with auto-DJ session information
    """
    # This is a simplified implementation - in a real app, this would be more sophisticated
    
    # Calculate number of tracks needed (assuming 3-4 minutes per track)
    avg_track_length = 3.5 * 60  # seconds
    num_tracks = max(1, int((duration * 60) / avg_track_length))
    
    # Build search filters
    filters = {}
    if genre_filter:
        filters["genre"] = genre_filter
    
    if target_bpm:
        # Allow some BPM variation
        bpm_range = target_bpm * 0.1  # ±10%
        filters["bpm_min"] = target_bpm - bpm_range
        filters["bpm_max"] = target_bpm + bpm_range
    
    if energy_level:
        # Map energy level to a range (0.0-1.0)
        energy_map = {
            "low": (0.0, 0.4),
            "medium": (0.3, 0.7),
            "high": (0.6, 0.9),
            "peak": (0.8, 1.0)
        }
        if energy_level.lower() in energy_map:
            min_e, max_e = energy_map[energy_level.lower()]
            filters["energy_min"] = min_e
            filters["energy_max"] = max_e
    
    # Search for matching tracks
    search_query = ""
    if mood:
        search_query = mood  # Simple mood-based search
    
    tracks = await search_tracks(
        query=search_query,
        limit=num_tracks * 2,  # Get more tracks than needed in case some fail to load
        **filters
    )
    
    if not tracks:
        return {
            "status": "error",
            "message": "No matching tracks found for the specified criteria"
        }
    
    # Create a playlist for the auto-DJ session
    try:
        playlist_manager = await get_playlist_manager()
        
        # Create a new playlist for this session
        playlist_name = f"Auto-DJ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if genre_filter:
            playlist_name += f" - {genre_filter}"
        
        # Create the playlist
        playlist = await playlist_manager.create_playlist(
            name=playlist_name,
            description=f"Auto-generated DJ mix ({duration} min)"
        )
        
        # Add tracks to the playlist
        added_tracks = 0
        for track in tracks[:num_tracks]:
            track_path = track.get('path')
            if track_path and os.path.exists(track_path):
                success = await playlist_manager.add_track(
                    playlist_id=playlist.id,
                    track_path=track_path,
                    position=added_tracks
                )
                if success:
                    added_tracks += 1
        
        return {
            "status": "success",
            "message": f"Created auto-DJ playlist with {added_tracks} tracks",
            "playlist_id": playlist.id,
            "playlist_name": playlist_name,
            "duration_minutes": duration,
            "genre_filter": genre_filter,
            "target_bpm": target_bpm,
            "energy_level": energy_level,
            "mood": mood,
            "tracks_added": added_tracks,
            "total_tracks_found": len(tracks)
        }
        
    except Exception as e:
        console.print(f"[red]Error creating auto-DJ playlist: {str(e)}[/red]")
        return {
            "status": "error",
            "message": f"Failed to create auto-DJ playlist: {str(e)}"
        }
# ==================== MAIN APPLICATION ====================

async def main():
    """Main application entry point"""
    global config, vdj_client, automation_engine, recording_service
    
    try:
        # Initialize configuration
        config = VDJConfig.from_env()
        
        console.print("[green]VirtualDJ-MCP Server starting...[/green]")
        console.print(f"[blue]VirtualDJ Path: {config.virtualdj_path}[/blue]")
        console.print(f"[blue]API URL: {config.rest_api_url}[/blue]")
        
        # Initialize VirtualDJ client
        vdj_client = VirtualDJClient(config)
        
        # Initialize services
        library_scanner = LibraryScanner()
        AudioAnalyzer()
        playlist_manager = PlaylistManager()
        
        # Initialize Automation Engine
        automation_engine = AutomationEngine(
            vdj_client=vdj_client,
            library_service=library_scanner,
            playlist_manager=playlist_manager
        )
        
        # Set up Auto-DJ tools
        from .tools.auto_dj_tools import setup_auto_dj_tools
        setup_auto_dj_tools(mcp, automation_engine)
        
        # Initialize Recording Service
        recording_service = RecordingService(
            output_dir=os.path.join(config.data_dir, "recordings")
        )
        
        # Set up Recording tools
        from .tools.recording_tools import setup_recording_tools
        setup_recording_tools(mcp, recording_service)
        
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
