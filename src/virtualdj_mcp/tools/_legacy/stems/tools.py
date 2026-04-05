"""
Stem separation tools for VirtualDJ MCP

VirtualDJ's Stems 2.0 engine allows real-time isolation of:
- Vocals
- Instrumental (everything except vocals)
- Bass
- Drums (kick, hihat, snare)
- Hi-hats
- Melody/synths
"""

from typing import Literal

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)

# Valid stem types
StemType = Literal["vocal", "instru", "bass", "drums", "hihat", "kick", "snare", "melody"]


def setup_stem_tools(mcp: FastMCP):
    """Set up stem separation MCP tools."""

    @mcp.tool()
    async def stem_kill(
        deck_id: int,
        stem: str,
        kill: bool = True
    ) -> dict:
        """
        Kill (mute) or restore a specific stem on a deck.

        Args:
            deck_id: Deck number (1-4)
            stem: Stem type - vocal, instru, bass, drums, hihat, kick, snare, melody
            kill: True to mute, False to restore

        Returns:
            Operation result

        Examples:
            stem_kill(1, "vocal", True)   # Mute vocals = instant instrumental
            stem_kill(1, "instru", True)  # Mute instrumental = instant acapella
            stem_kill(1, "bass", True)    # Kill the bass for buildup
        """
        try:
            client = await get_vdj_client()

            action = "kill" if kill else "unkill"
            cmd = f"deck {deck_id} stem_{action} '{stem}'"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    state = "killed" if kill else "restored"
                    console.print(f"[green]Deck {deck_id}: {stem} {state}[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "stem": stem,
                        "killed": kill
                    }
                else:
                    raise VDJError(f"Failed to {action} stem: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in stem_kill: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def stem_volume(
        deck_id: int,
        stem: str,
        volume: int
    ) -> dict:
        """
        Set the volume of a specific stem (0-100).

        Args:
            deck_id: Deck number (1-4)
            stem: Stem type - vocal, instru, bass, drums, hihat, kick, melody
            volume: Volume level 0-100

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()

            volume = max(0, min(100, volume))
            cmd = f"deck {deck_id} stem_volume '{stem}' {volume}%"

            async with client:
                result = await client.send_command(cmd)

                if result["status"] == "success":
                    console.print(f"[green]Deck {deck_id}: {stem} volume = {volume}%[/green]")
                    return {
                        "success": True,
                        "deck": deck_id,
                        "stem": stem,
                        "volume": volume
                    }
                else:
                    raise VDJError(f"Failed to set stem volume: {result.get('error')}")

        except Exception as e:
            console.print(f"[red]Error in stem_volume: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def acapella_mode(
        deck_id: int,
        enable: bool = True
    ) -> dict:
        """
        Enable acapella mode (vocals only) on a deck.

        Args:
            deck_id: Deck number (1-4)
            enable: True for acapella, False to restore full track

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()

            async with client:
                if enable:
                    # Kill instrumental, keep vocals
                    await client.send_command(f"deck {deck_id} stem_kill 'instru'")
                    console.print(f"[green]Deck {deck_id}: Acapella mode ON 🎤[/green]")
                else:
                    # Restore instrumental
                    await client.send_command(f"deck {deck_id} stem_unkill 'instru'")
                    console.print(f"[green]Deck {deck_id}: Acapella mode OFF[/green]")

                return {
                    "success": True,
                    "deck": deck_id,
                    "acapella": enable
                }

        except Exception as e:
            console.print(f"[red]Error in acapella_mode: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def instrumental_mode(
        deck_id: int,
        enable: bool = True
    ) -> dict:
        """
        Enable instrumental mode (no vocals) on a deck.

        Args:
            deck_id: Deck number (1-4)
            enable: True for instrumental, False to restore vocals

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()

            async with client:
                if enable:
                    await client.send_command(f"deck {deck_id} stem_kill 'vocal'")
                    console.print(f"[green]Deck {deck_id}: Instrumental mode ON 🎵[/green]")
                else:
                    await client.send_command(f"deck {deck_id} stem_unkill 'vocal'")
                    console.print(f"[green]Deck {deck_id}: Instrumental mode OFF[/green]")

                return {
                    "success": True,
                    "deck": deck_id,
                    "instrumental": enable
                }

        except Exception as e:
            console.print(f"[red]Error in instrumental_mode: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def isolate_drums(
        deck_id: int,
        enable: bool = True
    ) -> dict:
        """
        Isolate just the drums (kill everything else).

        Args:
            deck_id: Deck number (1-4)
            enable: True to isolate drums, False to restore

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()

            async with client:
                if enable:
                    await client.send_command(f"deck {deck_id} stem_kill 'vocal'")
                    await client.send_command(f"deck {deck_id} stem_kill 'melody'")
                    await client.send_command(f"deck {deck_id} stem_kill 'bass'")
                    console.print(f"[green]Deck {deck_id}: Drums isolated 🥁[/green]")
                else:
                    await client.send_command(f"deck {deck_id} stem_unkill 'vocal'")
                    await client.send_command(f"deck {deck_id} stem_unkill 'melody'")
                    await client.send_command(f"deck {deck_id} stem_unkill 'bass'")
                    console.print(f"[green]Deck {deck_id}: Full track restored[/green]")

                return {
                    "success": True,
                    "deck": deck_id,
                    "drums_isolated": enable
                }

        except Exception as e:
            console.print(f"[red]Error in isolate_drums: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def stem_swap(
        deck_a: int,
        deck_b: int,
        stem: str
    ) -> dict:
        """
        Swap a stem between two decks (e.g., vocals from deck A over instrumental from deck B).

        Args:
            deck_a: Source deck for the stem
            deck_b: Deck to mute that stem on
            stem: Stem type to swap

        Returns:
            Operation result

        Example:
            stem_swap(1, 2, "vocal")  # Vocals from deck 1, instrumental from deck 2
        """
        try:
            client = await get_vdj_client()

            async with client:
                # Kill the stem on deck B, keep it on deck A
                if stem == "vocal":
                    await client.send_command(f"deck {deck_a} stem_kill 'instru'")  # Acapella from A
                    await client.send_command(f"deck {deck_b} stem_kill 'vocal'")   # Instrumental from B
                else:
                    await client.send_command(f"deck {deck_a} stem_unkill '{stem}'")
                    await client.send_command(f"deck {deck_b} stem_kill '{stem}'")

                console.print(f"[green]Stem swap: {stem} from deck {deck_a} over deck {deck_b}[/green]")
                return {
                    "success": True,
                    "stem": stem,
                    "source_deck": deck_a,
                    "target_deck": deck_b
                }

        except Exception as e:
            console.print(f"[red]Error in stem_swap: {e}[/red]")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    async def reset_all_stems(deck_id: int) -> dict:
        """
        Reset all stems to full volume (unkill everything).

        Args:
            deck_id: Deck number (1-4)

        Returns:
            Operation result
        """
        try:
            client = await get_vdj_client()
            stems = ["vocal", "instru", "bass", "drums", "hihat", "kick", "melody"]

            async with client:
                for stem in stems:
                    await client.send_command(f"deck {deck_id} stem_unkill '{stem}'")

                console.print(f"[green]Deck {deck_id}: All stems restored[/green]")
                return {
                    "success": True,
                    "deck": deck_id,
                    "message": "All stems restored to full volume"
                }

        except Exception as e:
            console.print(f"[red]Error in reset_all_stems: {e}[/red]")
            return {"success": False, "error": str(e)}

