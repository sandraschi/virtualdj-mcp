"""
VDJ Deck Portmanteau Tool

Consolidates deck control operations into a single interface.
Operations: play, pause, toggle, load, seek, volume, status, load_security
"""

from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union
import asyncio

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError
from ..deck_control.models import DeckStatus

console = Console(file=__import__('sys').stderr)


def setup_deck_portmanteau(mcp: FastMCP):
    """Register vdj_deck portmanteau tool."""

    @mcp.tool()
    async def vdj_deck(
        operation: Literal["play", "pause", "toggle", "stop", "load", "seek", "volume", "status", "load_security"],
        deck_id: int = 1,
        track_path: Optional[str] = None,
        position: Optional[Union[float, str]] = None,
        volume: Optional[int] = None,
        force: bool = True,
        security_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive deck control for VirtualDJ.

        PORTMANTEAU PATTERN: Consolidates 6 deck tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - play: Start playback on deck
        - pause: Pause playback on deck
        - toggle: Toggle play/pause
        - stop: Stop playback completely
        - load: Load a track to deck (requires track_path)
        - seek: Seek to position (requires position - seconds or "50%")
        - volume: Set deck volume (requires volume 0-100)
        - status: Get current deck status
        - load_security: Set load security mode (requires security_mode: off/on/always)

        Args:
            operation: The deck operation to perform
            deck_id: Deck number (1-8, default: 1)
            track_path: Path to audio file (required for load operation)
            position: Seek position - seconds (float) or percentage ("50%")
            volume: Volume level 0-100 (required for volume operation)
            force: Stop playing deck before loading (default: True, prevents popup)
            security_mode: Load security mode: "off", "on", "always"

        Returns:
            Dict with operation result and deck status

        Examples:
            vdj_deck("play", deck_id=1)
            vdj_deck("load", deck_id=1, track_path="C:/Music/track.mp3")
            vdj_deck("seek", deck_id=1, position="50%")
            vdj_deck("volume", deck_id=1, volume=80)
            vdj_deck("status", deck_id=1)
            vdj_deck("load_security", security_mode="off")
        """
        try:
            client = await get_vdj_client()

            if operation == "play":
                async with client:
                    result = await client.send_command(f"deck {deck_id} play")
                    if result["status"] != "success":
                        raise VDJError(f"Failed to play deck {deck_id}")
                    console.print(f"[green]Deck {deck_id}: Playing[/green]")
                    return {"success": True, "operation": "play", "deck_id": deck_id}

            elif operation == "pause":
                async with client:
                    result = await client.send_command(f"deck {deck_id} pause")
                    if result["status"] != "success":
                        raise VDJError(f"Failed to pause deck {deck_id}")
                    console.print(f"[green]Deck {deck_id}: Paused[/green]")
                    return {"success": True, "operation": "pause", "deck_id": deck_id}

            elif operation == "toggle":
                async with client:
                    result = await client.send_command(f"deck {deck_id} play_pause")
                    if result["status"] != "success":
                        raise VDJError(f"Failed to toggle deck {deck_id}")
                    console.print(f"[green]Deck {deck_id}: Toggled[/green]")
                    return {"success": True, "operation": "toggle", "deck_id": deck_id}

            elif operation == "stop":
                async with client:
                    result = await client.send_command(f"deck {deck_id} stop")
                    if result["status"] != "success":
                        raise VDJError(f"Failed to stop deck {deck_id}")
                    console.print(f"[green]Deck {deck_id}: Stopped[/green]")
                    return {"success": True, "operation": "stop", "deck_id": deck_id}

            elif operation == "load":
                if not track_path:
                    return {"success": False, "error": "track_path required for load operation"}
                
                path = Path(track_path)
                if not path.exists():
                    raise VDJError(f"Track file not found: {track_path}")

                normalized_path = str(path).replace("\\", "/")

                async with client:
                    if force:
                        status_result = await client.query(f"deck {deck_id} get_isplaying")
                        if status_result.get("status") == "success":
                            is_playing = status_result.get("result", "0") in ("1", "true", "True")
                            if is_playing:
                                await client.send_command(f"deck {deck_id} stop")
                                await asyncio.sleep(0.2)

                    cmd = f"deck {deck_id} load '{normalized_path}'"
                    result = await client.send_command(cmd)

                    if result["status"] != "success":
                        raise VDJError(f"Failed to load track to deck {deck_id}")

                    console.print(f"[green]Loaded '{path.name}' to deck {deck_id}[/green]")
                    await asyncio.sleep(1)
                    
                    return {
                        "success": True,
                        "operation": "load",
                        "deck_id": deck_id,
                        "track": path.name
                    }

            elif operation == "seek":
                if position is None:
                    return {"success": False, "error": "position required for seek operation"}
                
                if isinstance(position, str) and position.endswith('%'):
                    cmd = f"deck {deck_id} goto {position}"
                else:
                    cmd = f"deck {deck_id} goto {position}s"

                async with client:
                    result = await client.send_command(cmd)
                    if result["status"] != "success":
                        raise VDJError(f"Failed to seek deck {deck_id}")
                    console.print(f"[green]Deck {deck_id} seeked to {position}[/green]")
                    return {"success": True, "operation": "seek", "deck_id": deck_id, "position": position}

            elif operation == "volume":
                if volume is None:
                    return {"success": False, "error": "volume required for volume operation"}
                
                vol = max(0, min(100, volume))
                async with client:
                    result = await client.send_command(f"deck {deck_id} volume {vol}%")
                    if result["status"] != "success":
                        raise VDJError(f"Failed to set deck {deck_id} volume")
                    console.print(f"[green]Deck {deck_id} volume set to {vol}%[/green]")
                    return {"success": True, "operation": "volume", "deck_id": deck_id, "volume": vol}

            elif operation == "status":
                async with client:
                    queries = {
                        "is_playing": f"deck {deck_id} get_isplaying",
                        "title": f"deck {deck_id} get_title",
                        "artist": f"deck {deck_id} get_artist",
                        "filepath": f"deck {deck_id} get_filepath",
                        "position": f"deck {deck_id} get_position",
                        "duration": f"deck {deck_id} get_songlength",
                        "bpm": f"deck {deck_id} get_bpm",
                        "key": f"deck {deck_id} get_key",
                        "volume": f"deck {deck_id} get_volume",
                        "pitch": f"deck {deck_id} get_pitch"
                    }

                    results = {}
                    for key, script in queries.items():
                        result = await client.query(script)
                        if result["status"] == "success":
                            results[key] = result["result"]

                    def safe_float(val, default=0.0):
                        try:
                            return float(val) if val else default
                        except (ValueError, TypeError):
                            return default

                    return {
                        "success": True,
                        "operation": "status",
                        "deck_id": deck_id,
                        "is_playing": results.get('is_playing', '0') == '1',
                        "track_title": results.get('title') or 'No Track',
                        "track_artist": results.get('artist') or 'Unknown',
                        "track_path": results.get('filepath'),
                        "position": safe_float(results.get('position')),
                        "duration": safe_float(results.get('duration')),
                        "bpm": safe_float(results.get('bpm')) or None,
                        "key": results.get('key'),
                        "volume": int(safe_float(results.get('volume'), 100)),
                        "pitch": safe_float(results.get('pitch'))
                    }

            elif operation == "load_security":
                if not security_mode:
                    return {"success": False, "error": "security_mode required (off/on/always)"}
                
                mode_map = {"off": "off", "none": "off", "on": "on", "ask": "on", "always": "always", "block": "always"}
                normalized_mode = mode_map.get(security_mode.lower())
                if not normalized_mode:
                    return {"success": False, "error": f"Invalid mode '{security_mode}'. Use: off, on, or always"}

                async with client:
                    result = await client.send_command(f"setting loadSecurity {normalized_mode}")
                    if result["status"] == "success":
                        console.print(f"[green]Load security set to: {normalized_mode}[/green]")
                        return {"success": True, "operation": "load_security", "mode": normalized_mode}
                    else:
                        return {"success": False, "error": result.get("error", "Failed to set load security")}

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_deck: {e}[/red]")
            return {"success": False, "error": str(e)}

