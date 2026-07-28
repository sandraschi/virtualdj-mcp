"""
VDJ Stems Portmanteau Tool

Consolidates stem separation operations into a single interface.
Operations: kill, unkill, volume, acapella, instrumental, isolate_drums, swap, reset, sample_stem
"""

import asyncio
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__("sys").stderr)


def setup_stems_portmanteau(mcp: FastMCP):
    """Register vdj_stems portmanteau tool."""

    @mcp.tool()
    async def vdj_stems(
        operation: Literal[
            "kill",
            "unkill",
            "volume",
            "acapella",
            "instrumental",
            "isolate_drums",
            "swap",
            "reset",
            "sample_stem",
        ],
        deck_id: int = 1,
        stem: str | None = None,
        volume: int | None = None,
        enable: bool = True,
        deck_a: int | None = None,
        deck_b: int | None = None,
        slot: int = 1,
    ) -> dict[str, Any]:
        """
        Stem separation control for VirtualDJ.

        VirtualDJ's Stems 2.0 engine allows real-time isolation of:
        - vocal: Vocals
        - instru: Instrumental (everything except vocals)
        - bass: Bass frequencies
        - drums: Full drum kit
        - hihat: Hi-hats
        - kick: Kick drum
        - snare: Snare drum
        - melody: Melody/synths

        PORTMANTEAU PATTERN: Consolidates 8 stem tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - kill: Mute a specific stem (requires stem)
        - unkill: Restore a specific stem (requires stem)
        - volume: Set stem volume 0-100 (requires stem, volume)
        - acapella: Toggle acapella mode (vocals only)
        - instrumental: Toggle instrumental mode (no vocals)
        - isolate_drums: Isolate drums only
        - swap: Swap a stem between two decks (requires stem, deck_a, deck_b)
        - reset: Reset all stems to full volume
        - sample_stem: Record the active stems/solo from deck directly to sampler slot (requires slot)

        Args:
            operation: The stem operation to perform
            deck_id: Deck number (1-8, default: 1)
            stem: Stem type (vocal, instru, bass, drums, hihat, kick, snare, melody)
            volume: Volume level 0-100 (for volume operation)
            enable: Enable/disable mode (for acapella/instrumental/isolate_drums)
            deck_a: Source deck for swap operation
            deck_b: Target deck for swap operation
            slot: Sampler slot number to record into (for sample_stem operation, default: 1)

        Returns:
            Dict with operation result

        Examples:
            vdj_stems("kill", deck_id=1, stem="vocal")       # Instant instrumental
            vdj_stems("acapella", deck_id=1, enable=True)
            vdj_stems("sample_stem", deck_id=1, slot=2)      # Record isolated stem to sampler slot 2
            vdj_stems("reset", deck_id=1)
        """
        try:
            client = await get_vdj_client()

            if operation == "kill":
                if not stem:
                    return {"success": False, "error": "stem required for kill operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_id} stem_kill '{stem}'")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: {stem} killed[/green]")
                        return {"success": True, "operation": "kill", "deck_id": deck_id, "stem": stem, "killed": True}
                    else:
                        raise VDJError(f"Failed to kill stem: {result.get('error')}")

            elif operation == "unkill":
                if not stem:
                    return {"success": False, "error": "stem required for unkill operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_id} stem_unkill '{stem}'")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: {stem} restored[/green]")
                        return {
                            "success": True,
                            "operation": "unkill",
                            "deck_id": deck_id,
                            "stem": stem,
                            "killed": False,
                        }
                    else:
                        raise VDJError(f"Failed to unkill stem: {result.get('error')}")

            elif operation == "volume":
                if not stem or volume is None:
                    return {"success": False, "error": "stem and volume required for volume operation"}

                vol = max(0, min(100, volume))
                async with client:
                    result = await client.send_command(f"deck {deck_id} stem_volume '{stem}' {vol}%")
                    if result["status"] == "success":
                        console.print(f"[green]Deck {deck_id}: {stem} volume = {vol}%[/green]")
                        return {"success": True, "operation": "volume", "deck_id": deck_id, "stem": stem, "volume": vol}
                    else:
                        raise VDJError(f"Failed to set stem volume: {result.get('error')}")

            elif operation == "acapella":
                async with client:
                    if enable:
                        await client.send_command(f"deck {deck_id} stem_kill 'instru'")
                        console.print(f"[green]Deck {deck_id}: Acapella mode ON 🎤[/green]")
                    else:
                        await client.send_command(f"deck {deck_id} stem_unkill 'instru'")
                        console.print(f"[green]Deck {deck_id}: Acapella mode OFF[/green]")

                    return {"success": True, "operation": "acapella", "deck_id": deck_id, "enabled": enable}

            elif operation == "instrumental":
                async with client:
                    if enable:
                        await client.send_command(f"deck {deck_id} stem_kill 'vocal'")
                        console.print(f"[green]Deck {deck_id}: Instrumental mode ON 🎵[/green]")
                    else:
                        await client.send_command(f"deck {deck_id} stem_unkill 'vocal'")
                        console.print(f"[green]Deck {deck_id}: Instrumental mode OFF[/green]")

                    return {"success": True, "operation": "instrumental", "deck_id": deck_id, "enabled": enable}

            elif operation == "isolate_drums":
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

                    return {"success": True, "operation": "isolate_drums", "deck_id": deck_id, "enabled": enable}

            elif operation == "swap":
                if not stem or not deck_a or not deck_b:
                    return {"success": False, "error": "stem, deck_a, and deck_b required for swap operation"}

                async with client:
                    if stem == "vocal":
                        await client.send_command(f"deck {deck_a} stem_kill 'instru'")
                        await client.send_command(f"deck {deck_b} stem_kill 'vocal'")
                    else:
                        await client.send_command(f"deck {deck_a} stem_unkill '{stem}'")
                        await client.send_command(f"deck {deck_b} stem_kill '{stem}'")

                    console.print(f"[green]Stem swap: {stem} from deck {deck_a} over deck {deck_b}[/green]")
                    return {
                        "success": True,
                        "operation": "swap",
                        "stem": stem,
                        "source_deck": deck_a,
                        "target_deck": deck_b,
                    }

            elif operation == "reset":
                stems = ["vocal", "instru", "bass", "drums", "hihat", "kick", "melody"]
                async with client:
                    for s in stems:
                        await client.send_command(f"deck {deck_id} stem_unkill '{s}'")

                    console.print(f"[green]Deck {deck_id}: All stems restored[/green]")
                    return {"success": True, "operation": "reset", "deck_id": deck_id}

            elif operation == "sample_stem":
                async with client:
                    # Let's start the recording
                    result_start = await client.send_command(f"sampler {slot} start_rec")
                    if result_start["status"] != "success":
                        raise VDJError(f"Failed to start sampler recording: {result_start.get('error')}")

                    console.print(f"[green]Deck {deck_id}: Started recording stem into sampler slot {slot}...[/green]")

                    # Wait for a brief period to capture the loop (e.g., 4 seconds)
                    await asyncio.sleep(4.0)

                    result_stop = await client.send_command(f"sampler {slot} stop_rec")
                    if result_stop["status"] != "success":
                        raise VDJError(f"Failed to stop sampler recording: {result_stop.get('error')}")

                    console.print(f"[green]Deck {deck_id}: Saved stem sample to sampler slot {slot}[/green]")
                    return {
                        "success": True,
                        "operation": "sample_stem",
                        "deck_id": deck_id,
                        "sampler_slot": slot,
                        "duration_seconds": 4.0,
                    }

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_stems: {e}[/red]")
            return {"success": False, "error": str(e)}
