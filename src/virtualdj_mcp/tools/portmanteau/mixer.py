"""
VDJ Mixer Portmanteau Tool

Consolidates mixing operations into a single interface.
Operations: crossfader, sync, eq_high, eq_mid, eq_low, gain
"""

from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)


def setup_mixer_portmanteau(mcp: FastMCP):
    """Register vdj_mixer portmanteau tool."""

    @mcp.tool()
    async def vdj_mixer(
        operation: Literal["crossfader", "sync", "eq_high", "eq_mid", "eq_low", "gain", "filter"],
        position: Optional[float] = None,
        deck_a: Optional[int] = None,
        deck_b: Optional[int] = None,
        deck_id: Optional[int] = None,
        value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive mixer control for VirtualDJ.

        PORTMANTEAU PATTERN: Consolidates mixer tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - crossfader: Set crossfader position (-100 to +100, 0 = center)
        - sync: Sync BPM between two decks (requires deck_a, deck_b)
        - eq_high: Set high EQ for deck (requires deck_id, value 0-100)
        - eq_mid: Set mid EQ for deck (requires deck_id, value 0-100)
        - eq_low: Set low/bass EQ for deck (requires deck_id, value 0-100)
        - gain: Set deck gain (requires deck_id, value 0-150)
        - filter: Set filter for deck (requires deck_id, value 0-100)

        Args:
            operation: The mixer operation to perform
            position: Crossfader position -100 to +100 (for crossfader operation)
            deck_a: Source deck for sync operation
            deck_b: Target deck for sync operation
            deck_id: Deck number for EQ/gain/filter operations
            value: Value for EQ/gain/filter (0-100, gain allows 0-150)

        Returns:
            Dict with operation result

        Examples:
            vdj_mixer("crossfader", position=0)        # Center crossfader
            vdj_mixer("crossfader", position=-100)    # Full left (deck A)
            vdj_mixer("sync", deck_a=1, deck_b=2)     # Sync deck 2 to deck 1
            vdj_mixer("eq_high", deck_id=1, value=75) # Set high EQ
            vdj_mixer("eq_low", deck_id=2, value=50)  # Set bass EQ
        """
        try:
            client = await get_vdj_client()

            if operation == "crossfader":
                if position is None:
                    return {"success": False, "error": "position required for crossfader operation"}
                
                pos = max(-100, min(100, position))
                vdj_position = (pos + 100) / 2  # Convert to VDJ's 0-100 scale

                async with client:
                    result = await client.send_command(f"crossfader {vdj_position}%")
                    if result["status"] != "success":
                        raise VDJError("Failed to set crossfader")
                    
                    console.print(f"[green]Crossfader set to {pos}[/green]")
                    return {
                        "success": True,
                        "operation": "crossfader",
                        "position": pos,
                        "vdj_value": vdj_position
                    }

            elif operation == "sync":
                if not deck_a or not deck_b:
                    return {"success": False, "error": "deck_a and deck_b required for sync operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_b} sync deck {deck_a}")
                    if result["status"] != "success":
                        raise VDJError("Failed to sync decks")

                    # Get BPMs to confirm sync
                    bpm_a = await client.query(f"deck {deck_a} get_bpm")
                    bpm_b = await client.query(f"deck {deck_b} get_bpm")

                    console.print(f"[green]Synced deck {deck_b} to deck {deck_a} BPM[/green]")
                    return {
                        "success": True,
                        "operation": "sync",
                        "deck_a": deck_a,
                        "deck_b": deck_b,
                        "bpm_a": bpm_a.get("result"),
                        "bpm_b": bpm_b.get("result")
                    }

            elif operation in ("eq_high", "eq_mid", "eq_low"):
                if deck_id is None or value is None:
                    return {"success": False, "error": "deck_id and value required for EQ operation"}
                
                val = max(0, min(100, value))
                eq_map = {"eq_high": "eq_high", "eq_mid": "eq_mid", "eq_low": "eq_low"}
                eq_cmd = eq_map[operation]

                async with client:
                    result = await client.send_command(f"deck {deck_id} {eq_cmd} {val}%")
                    if result["status"] != "success":
                        raise VDJError(f"Failed to set {operation}")
                    
                    console.print(f"[green]Deck {deck_id} {operation} set to {val}%[/green]")
                    return {
                        "success": True,
                        "operation": operation,
                        "deck_id": deck_id,
                        "value": val
                    }

            elif operation == "gain":
                if deck_id is None or value is None:
                    return {"success": False, "error": "deck_id and value required for gain operation"}
                
                val = max(0, min(150, value))  # Gain can go to 150%

                async with client:
                    result = await client.send_command(f"deck {deck_id} gain {val}%")
                    if result["status"] != "success":
                        raise VDJError("Failed to set gain")
                    
                    console.print(f"[green]Deck {deck_id} gain set to {val}%[/green]")
                    return {
                        "success": True,
                        "operation": "gain",
                        "deck_id": deck_id,
                        "value": val
                    }

            elif operation == "filter":
                if deck_id is None or value is None:
                    return {"success": False, "error": "deck_id and value required for filter operation"}
                
                val = max(0, min(100, value))

                async with client:
                    result = await client.send_command(f"deck {deck_id} filter {val}%")
                    if result["status"] != "success":
                        raise VDJError("Failed to set filter")
                    
                    console.print(f"[green]Deck {deck_id} filter set to {val}%[/green]")
                    return {
                        "success": True,
                        "operation": "filter",
                        "deck_id": deck_id,
                        "value": val
                    }

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_mixer: {e}[/red]")
            return {"success": False, "error": str(e)}

