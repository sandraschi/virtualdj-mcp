"""
VDJ Beatgrid Portmanteau Tool

Consolidates BPM, beatgrid, and loop operations into a single interface.
Operations: set_bpm, tap, adjust, anchor, pitch_bend, pitch_reset, beat_jump, loop, loop_roll, loop_exit
"""

from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)


def setup_beatgrid_portmanteau(mcp: FastMCP):
    """Register vdj_beatgrid portmanteau tool."""

    @mcp.tool()
    async def vdj_beatgrid(
        operation: Literal["set_bpm", "tap", "adjust", "anchor", "pitch_bend", "pitch_reset", "beat_jump", "loop", "loop_roll", "loop_exit"],
        deck_id: int = 1,
        bpm: float | None = None,
        adjustment: float | None = None,
        direction: str | None = None,
        amount: float = 4.0,
        beats: float | None = None
    ) -> dict[str, Any]:
        """
        BPM, beatgrid, and loop control for VirtualDJ.

        PORTMANTEAU PATTERN: Consolidates 10 beatgrid tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - set_bpm: Manually set BPM (60-200)
        - tap: Tap BPM - call repeatedly to tap out tempo
        - adjust: Shift beatgrid left/right (-100 to +100 ms)
        - anchor: Set current position as first beat
        - pitch_bend: Temporarily speed up/slow down (up/down, amount%)
        - pitch_reset: Reset pitch to 0% (original speed)
        - beat_jump: Jump forward/backward by beats
        - loop: Set a loop of specified beats
        - loop_roll: Temporary loop (returns to original position)
        - loop_exit: Exit current loop

        Args:
            operation: The beatgrid operation to perform
            deck_id: Deck number (1-4, default: 1)
            bpm: Target BPM for set_bpm (60-200)
            adjustment: Milliseconds to shift beatgrid (-100 to +100)
            direction: "up" or "down" for pitch_bend
            amount: Bend amount in percent (default: 4.0)
            beats: Number of beats for jump/loop operations

        Returns:
            Dict with operation result

        Examples:
            vdj_beatgrid("set_bpm", deck_id=1, bpm=128)
            vdj_beatgrid("tap", deck_id=1)  # Call repeatedly
            vdj_beatgrid("adjust", deck_id=1, adjustment=10)  # Shift 10ms right
            vdj_beatgrid("anchor", deck_id=1)
            vdj_beatgrid("pitch_bend", deck_id=1, direction="up", amount=4)
            vdj_beatgrid("pitch_reset", deck_id=1)
            vdj_beatgrid("beat_jump", deck_id=1, beats=8)  # Jump 8 beats forward
            vdj_beatgrid("beat_jump", deck_id=1, beats=-4) # Jump 4 beats back
            vdj_beatgrid("loop", deck_id=1, beats=4)
            vdj_beatgrid("loop_roll", deck_id=1, beats=0.5)
            vdj_beatgrid("loop_exit", deck_id=1)
        """
        try:
            client = await get_vdj_client()

            if operation == "set_bpm":
                if bpm is None:
                    return {"success": False, "error": "bpm required for set_bpm operation"}

                target_bpm = max(60.0, min(200.0, bpm))
                async with client:
                    result = await client.send_command(f"deck {deck_id} bpm {target_bpm}")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: BPM set to {target_bpm}[/green]")
                        return {"success": True, "operation": "set_bpm", "deck_id": deck_id, "bpm": target_bpm}
                    else:
                        raise VDJError(f"Failed to set BPM: {result.get('error')}")

            elif operation == "tap":
                async with client:
                    result = await client.send_command(f"deck {deck_id} bpm_tap")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: BPM tap[/green]")
                        return {"success": True, "operation": "tap", "deck_id": deck_id}
                    else:
                        raise VDJError(f"Failed to tap BPM: {result.get('error')}")

            elif operation == "adjust":
                if adjustment is None:
                    return {"success": False, "error": "adjustment required for adjust operation"}

                adj = max(-100, min(100, adjustment))
                async with client:
                    result = await client.send_command(f"deck {deck_id} beatgrid_adjust {adj}")
                    if result["status"] == "success":
                        direction_str = "right" if adj > 0 else "left"
                        console.print(f"[green]Deck {deck_id}: Beatgrid shifted {abs(adj)}ms {direction_str}[/green]")
                        return {"success": True, "operation": "adjust", "deck_id": deck_id, "adjustment_ms": adj}
                    else:
                        raise VDJError(f"Failed to adjust beatgrid: {result.get('error')}")

            elif operation == "anchor":
                async with client:
                    result = await client.send_command(f"deck {deck_id} beatgrid_anchor")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: Beatgrid anchored[/green]")
                        return {"success": True, "operation": "anchor", "deck_id": deck_id}
                    else:
                        raise VDJError(f"Failed to anchor beatgrid: {result.get('error')}")

            elif operation == "pitch_bend":
                if not direction:
                    return {"success": False, "error": "direction required for pitch_bend (up/down)"}

                if direction.lower() == "up":
                    cmd = f"deck {deck_id} pitch +{amount}%"
                else:
                    cmd = f"deck {deck_id} pitch -{amount}%"

                async with client:
                    result = await client.send_command(cmd)
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: Pitch bend {direction} {amount}%[/green]")
                        return {"success": True, "operation": "pitch_bend", "deck_id": deck_id, "direction": direction, "amount": amount}
                    else:
                        raise VDJError(f"Failed to pitch bend: {result.get('error')}")

            elif operation == "pitch_reset":
                async with client:
                    result = await client.send_command(f"deck {deck_id} pitch 0%")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: Pitch reset to 0%[/green]")
                        return {"success": True, "operation": "pitch_reset", "deck_id": deck_id}
                    else:
                        raise VDJError(f"Failed to reset pitch: {result.get('error')}")

            elif operation == "beat_jump":
                if beats is None:
                    return {"success": False, "error": "beats required for beat_jump operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_id} beatjump {int(beats)}")
                    if result["status"] == "success":
                        direction_str = "forward" if beats > 0 else "backward"
                        console.print(f"[green]Deck {deck_id}: Jumped {abs(int(beats))} beats {direction_str}[/green]")
                        return {"success": True, "operation": "beat_jump", "deck_id": deck_id, "beats": int(beats)}
                    else:
                        raise VDJError(f"Failed to beat jump: {result.get('error')}")

            elif operation == "loop":
                if beats is None:
                    return {"success": False, "error": "beats required for loop operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_id} loop {beats}")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: Loop set to {beats} beats[/green]")
                        return {"success": True, "operation": "loop", "deck_id": deck_id, "beats": beats}
                    else:
                        raise VDJError(f"Failed to set loop: {result.get('error')}")

            elif operation == "loop_roll":
                if beats is None:
                    return {"success": False, "error": "beats required for loop_roll operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_id} loop_roll {beats}")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: Loop roll {beats} beats[/green]")
                        return {"success": True, "operation": "loop_roll", "deck_id": deck_id, "beats": beats}
                    else:
                        raise VDJError(f"Failed to start loop roll: {result.get('error')}")

            elif operation == "loop_exit":
                async with client:
                    result = await client.send_command(f"deck {deck_id} loop_exit")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: Loop exited[/green]")
                        return {"success": True, "operation": "loop_exit", "deck_id": deck_id}
                    else:
                        raise VDJError(f"Failed to exit loop: {result.get('error')}")

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_beatgrid: {e}[/red]")
            return {"success": False, "error": str(e)}

