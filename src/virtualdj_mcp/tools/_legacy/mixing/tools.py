"""
Mixing tools for VirtualDJ MCP
"""

from typing import Any

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError
from .models import MixerStatus

# Initialize console for logging
console = Console(file=__import__('sys').stderr)


def setup_mixing_tools(mcp: FastMCP):
    """
    Set up mixing related MCP tools.

    Args:
        mcp: MCP instance to register tools with
    """

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
    async def auto_sync_decks(deck_a: int, deck_b: int) -> dict[str, Any]:
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
                from ..deck_control.tools import get_deck_status
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
