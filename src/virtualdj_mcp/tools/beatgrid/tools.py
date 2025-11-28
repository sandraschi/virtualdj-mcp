"""
Beatgrid tools for VirtualDJ MCP

Tools for manipulating beat grids, BPM, and beat alignment.
"""

from typing import Optional
from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)


def setup_beatgrid_tools(mcp: FastMCP):
    """Set up beatgrid MCP tools."""

    @mcp.tool()
    async def set_bpm(
        deck_id: int,
        bpm: float
    ) -> dict:
        """
        Manually set the BPM of a track.

        Args:
            deck_id: Deck number (1-4)
            bpm: Target BPM (60-200)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            
            bpm = max(60.0, min(200.0, bpm))
            cmd = f"deck {deck_id} bpm {bpm}"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: BPM set to {bpm}[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "bpm": bpm
                    }
                else:
                    raise VDJError(f"Failed to set BPM: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in set_bpm: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def tap_bpm(deck_id: int) -> dict:
        """
        Tap BPM - call this repeatedly to tap out the tempo.

        Args:
            deck_id: Deck number (1-4)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} bpm_tap"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: BPM tap[/green]")
                    return {"success": True, "deck": deck_id}
                else:
                    raise VDJError(f"Failed to tap BPM: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in tap_bpm: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def beatgrid_adjust(
        deck_id: int,
        adjustment: float
    ) -> dict:
        """
        Adjust the beatgrid position (shift beats left/right).

        Args:
            deck_id: Deck number (1-4)
            adjustment: Milliseconds to shift (-100 to +100)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            
            adjustment = max(-100, min(100, adjustment))
            cmd = f"deck {deck_id} beatgrid_adjust {adjustment}"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    direction = "right" if adjustment > 0 else "left"
                    console.print(f"[green]Deck {deck_id}: Beatgrid shifted {abs(adjustment)}ms {direction}[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "adjustment_ms": adjustment
                    }
                else:
                    raise VDJError(f"Failed to adjust beatgrid: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in beatgrid_adjust: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def beatgrid_anchor(deck_id: int) -> dict:
        """
        Set the current position as the first beat (anchor point).

        Args:
            deck_id: Deck number (1-4)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} beatgrid_anchor"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: Beatgrid anchored at current position[/green]")
                    return {"success": True, "deck": deck_id}
                else:
                    raise VDJError(f"Failed to anchor beatgrid: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in beatgrid_anchor: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def pitch_bend(
        deck_id: int,
        direction: str,
        amount: float = 4.0
    ) -> dict:
        """
        Temporarily bend the pitch (speed up or slow down).

        Args:
            deck_id: Deck number (1-4)
            direction: "up" to speed up, "down" to slow down
            amount: Bend amount in percent (default 4%)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            
            if direction.lower() == "up":
                cmd = f"deck {deck_id} pitch +{amount}%"
            else:
                cmd = f"deck {deck_id} pitch -{amount}%"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: Pitch bend {direction} {amount}%[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "direction": direction,
                        "amount": amount
                    }
                else:
                    raise VDJError(f"Failed to pitch bend: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in pitch_bend: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def pitch_reset(deck_id: int) -> dict:
        """
        Reset pitch to 0% (original speed).

        Args:
            deck_id: Deck number (1-4)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} pitch 0%"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: Pitch reset to 0%[/green]")
                    return {"success": True, "deck": deck_id}
                else:
                    raise VDJError(f"Failed to reset pitch: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in pitch_reset: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def beat_jump(
        deck_id: int,
        beats: int
    ) -> dict:
        """
        Jump forward or backward by a number of beats.

        Args:
            deck_id: Deck number (1-4)
            beats: Number of beats to jump (positive = forward, negative = backward)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} beatjump {beats}"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    direction = "forward" if beats > 0 else "backward"
                    console.print(f"[green]Deck {deck_id}: Jumped {abs(beats)} beats {direction}[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "beats": beats
                    }
                else:
                    raise VDJError(f"Failed to beat jump: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in beat_jump: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def loop_roll(
        deck_id: int,
        beats: float
    ) -> dict:
        """
        Start a loop roll (temporary loop that returns to original position when released).

        Args:
            deck_id: Deck number (1-4)
            beats: Loop length in beats (0.125, 0.25, 0.5, 1, 2, 4, 8, etc.)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} loop_roll {beats}"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: Loop roll {beats} beats[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "beats": beats
                    }
                else:
                    raise VDJError(f"Failed to start loop roll: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in loop_roll: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def loop_set(
        deck_id: int,
        beats: float
    ) -> dict:
        """
        Set a loop of specified beat length.

        Args:
            deck_id: Deck number (1-4)
            beats: Loop length in beats

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} loop {beats}"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: Loop set to {beats} beats[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "beats": beats
                    }
                else:
                    raise VDJError(f"Failed to set loop: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in loop_set: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def loop_exit(deck_id: int) -> dict:
        """
        Exit the current loop.

        Args:
            deck_id: Deck number (1-4)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            cmd = f"deck {deck_id} loop_exit"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: Loop exited[/green]")
                    return {"success": True, "deck": deck_id}
                else:
                    raise VDJError(f"Failed to exit loop: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in loop_exit: {e}[/red]")
            return {"success": False, "error": str(e)}

