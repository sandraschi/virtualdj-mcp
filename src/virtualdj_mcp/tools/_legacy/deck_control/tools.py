"""
Deck control tools for VirtualDJ MCP

Uses HTTP Network Control Plugin API for communication.
"""

from pathlib import Path

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError
from .models import DeckStatus

# Initialize console for logging
console = Console(file=__import__('sys').stderr)


def setup_deck_control_tools(mcp: FastMCP):
    """
    Set up deck control related MCP tools.

    Args:
        mcp: MCP instance to register tools with
    """

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
                return await get_deck_status(deck_id)

        except Exception as e:
            console.print(f"[red]Error in play_pause_deck: {e}[/red]")
            raise VDJError(str(e))


    @mcp.tool()
    async def load_track_to_deck(
        deck_id: int,
        track_path: str,
        force: bool = True
    ) -> DeckStatus:
        """
        Load a track to a specific deck

        Args:
            deck_id: Deck number (1-8)
            track_path: Path to audio file or library reference
            force: If True, stops deck if playing to avoid confirmation popup (default: True)

        Returns:
            Updated deck status with loaded track

        Note:
            By default, force=True will stop a playing deck before loading.
            This prevents VirtualDJ's loadSecurity popup from blocking automation.
            Set force=False if you want the popup to appear when loading on a playing deck.
        """
        try:
            client = await get_vdj_client()

            # Validate track path
            path = Path(track_path)
            if not path.exists():
                raise VDJError(f"Track file not found: {track_path}")

            # Normalize path for VDJScript (forward slashes)
            normalized_path = str(path).replace("\\", "/")

            async with client:
                if force:
                    # Check if deck is playing and stop it first to avoid popup
                    status_result = await client.query(f"deck {deck_id} get_isplaying")
                    if status_result.get("status") == "success":
                        is_playing = status_result.get("result", "0") in ("1", "true", "True")
                        if is_playing:
                            console.print(f"[yellow]Deck {deck_id} is playing, stopping first...[/yellow]")
                            await client.send_command(f"deck {deck_id} stop")
                            import asyncio
                            await asyncio.sleep(0.2)  # Brief pause for stop to take effect

                cmd = f"deck {deck_id} load '{normalized_path}'"
                result = await client.send_command(cmd)

                if result["status"] != "success":
                    raise VDJError(f"Failed to load track to deck {deck_id}: {result.get('error', 'Unknown error')}")

                console.print(f"[green]Loaded '{path.name}' to deck {deck_id}[/green]")

                # Wait a moment for track to load before getting status
                import asyncio
                await asyncio.sleep(1)

                return await get_deck_status(deck_id)

        except Exception as e:
            console.print(f"[red]Error in load_track_to_deck: {e}[/red]")
            raise VDJError(str(e))


    @mcp.tool()
    async def seek_deck(
        deck_id: int,
        position: float | str
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
                # Use proper VDJScript syntax for HTTP API
                # deck N get_xxx returns the value directly
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

                # Parse results into DeckStatus
                def safe_float(val, default=0.0):
                    try:
                        return float(val) if val else default
                    except (ValueError, TypeError):
                        return default

                def safe_int(val, default=0):
                    try:
                        return int(float(val)) if val else default
                    except (ValueError, TypeError):
                        return default

                return DeckStatus(
                    deck_id=deck_id,
                    is_playing=results.get('is_playing', '0') == '1' or results.get('is_playing', '').lower() == 'true',
                    track_path=results.get('filepath'),
                    track_title=results.get('title') or 'No Track',
                    track_artist=results.get('artist') or 'Unknown Artist',
                    position=safe_float(results.get('position')),
                    duration=safe_float(results.get('duration')),
                    bpm=safe_float(results.get('bpm')) if results.get('bpm') else None,
                    key=results.get('key') or None,
                    volume=safe_int(results.get('volume'), 100),
                    pitch=safe_float(results.get('pitch'))
                )

        except Exception as e:
            console.print(f"[red]Error in get_deck_status: {e}[/red]")
            # Return a default deck status on error
            return DeckStatus(
                deck_id=deck_id,
                is_playing=False
            )


    @mcp.tool()
    async def set_load_security(mode: str) -> dict:
        """
        Set VirtualDJ's load security mode for loading tracks on playing decks.

        Args:
            mode: Security mode - "off" (no popup), "on" (ask), or "always" (block)
                - "off" / "none": Load tracks without confirmation (best for automation)
                - "on" / "ask": Show confirmation popup when loading on playing deck
                - "always" / "block": Prevent loading on playing decks entirely

        Returns:
            dict with success status and current setting

        Note:
            For MCP automation, "off" is recommended to prevent popup dialogs.
            The load_track_to_deck tool has force=True by default which stops
            the deck before loading, but this setting affects all load operations.
        """
        try:
            client = await get_vdj_client()

            # Normalize mode names
            mode_map = {
                "off": "off",
                "none": "off",
                "on": "on",
                "ask": "on",
                "always": "always",
                "block": "always"
            }

            normalized_mode = mode_map.get(mode.lower())
            if not normalized_mode:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Use: off, on, or always"
                }

            async with client:
                # Set the loadSecurity setting
                result = await client.send_command(f"setting loadSecurity {normalized_mode}")

                if result["status"] == "success":
                    console.print(f"[green]Load security set to: {normalized_mode}[/green]")

                    # Verify the setting
                    verify = await client.query("setting loadSecurity")
                    current = verify.get("result", "unknown")

                    return {
                        "success": True,
                        "mode": normalized_mode,
                        "current_setting": current,
                        "message": f"Load security set to '{normalized_mode}'"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Failed to set load security")
                    }

        except Exception as e:
            console.print(f"[red]Error in set_load_security: {e}[/red]")
            return {
                "success": False,
                "error": str(e)
            }
