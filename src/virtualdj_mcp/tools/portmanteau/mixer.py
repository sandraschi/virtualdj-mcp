"""
VDJ Mixer Portmanteau Tool

Consolidates mixing operations into a single interface.
Operations: crossfader, sync, eq_high, eq_mid, eq_low, gain, filter, master_volume, headphone_volume, headphone_mix, effect, eq_reset
"""

from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client
from ..shared.exceptions import VDJError

console = Console(file=__import__('sys').stderr)


def setup_mixer_portmanteau(mcp: FastMCP):
    """Register vdj_mixer portmanteau tool."""

    @mcp.tool()
    async def vdj_mixer(
        operation: Literal[
            "crossfader",
            "sync",
            "eq_high",
            "eq_mid",
            "eq_low",
            "gain",
            "filter",
            "master_volume",
            "headphone_volume",
            "headphone_mix",
            "effect",
            "eq_reset",
        ],
        position: float | None = None,
        deck_a: int | None = None,
        deck_b: int | None = None,
        deck_id: int | None = None,
        value: float | None = None,
        effect_slot: int = 0,
        effect_type: str | None = None,
        enable: bool = True,
        wet_dry: float = 50.0,
        param1: float = 0.0,
        param2: float = 0.0,
    ) -> dict[str, Any]:
        """
        Comprehensive mixer control for VirtualDJ.

        PORTMANTEAU PATTERN: Consolidates all mixer and EQ tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - crossfader: Set crossfader position (-100 to +100, 0 = center)
        - sync: Sync BPM between two decks (requires deck_a, deck_b)
        - eq_high: Set high EQ for deck (requires deck_id, value 0-100)
        - eq_mid: Set mid EQ for deck (requires deck_id, value 0-100)
        - eq_low: Set low/bass EQ for deck (requires deck_id, value 0-100)
        - gain: Set deck gain (requires deck_id, value 0-150)
        - filter: Set filter for deck (requires deck_id, value 0-100)
        - master_volume: Set overall master volume (requires value 0-100)
        - headphone_volume: Set headphone cue volume (requires value 0-100)
        - headphone_mix: Set cue/master mix in headphones (requires value 0-100)
        - effect: Configure audio effects (requires deck_id, effect_type)
        - eq_reset: Reset EQ back to flat 0dB (requires deck_id)

        Args:
            operation: The mixer operation to perform
            position: Crossfader position -100 to +100 (for crossfader operation)
            deck_a: Source deck for sync operation
            deck_b: Target deck for sync operation
            deck_id: Deck number for EQ/gain/filter/effect operations
            value: Numeric value for EQ, volume, gain, filter, or mix
            effect_slot: Effect slot 0-2 (default: 0)
            effect_type: Name of VirtualDJ audio effect (e.g., "echo", "flanger")
            enable: Enable or disable the effect (for effect operation)
            wet_dry: Wet/dry mix percentage 0-100 (for effect operation)
            param1: Effect parameter 1 (0.0 to 1.0)
            param2: Effect parameter 2 (0.0 to 1.0)

        Returns:
            Dict with operation result

        Examples:
            vdj_mixer("crossfader", position=0)        # Center crossfader
            vdj_mixer("eq_high", deck_id=1, value=75) # Set high EQ
            vdj_mixer("master_volume", value=80)      # Set master volume to 80%
            vdj_mixer("effect", deck_id=1, effect_type="echo", enable=True) # Turn echo on
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

            elif operation == "master_volume":
                if value is None:
                    return {"success": False, "error": "value required for master_volume operation"}

                val = max(0, min(100, int(value)))

                async with client:
                    result = await client.send_command(f"mastervolume {val}%")
                    if result["status"] != "success":
                        raise VDJError("Failed to set master volume")

                    console.print(f"[green]Master volume set to {val}%[/green]")
                    return {
                        "success": True,
                        "operation": "master_volume",
                        "value": val
                    }

            elif operation == "headphone_volume":
                if value is None:
                    return {"success": False, "error": "value required for headphone_volume operation"}

                val = max(0, min(100, int(value)))

                async with client:
                    result = await client.send_command(f"headphone {val}%")
                    if result["status"] != "success":
                        raise VDJError("Failed to set headphone volume")

                    console.print(f"[green]Headphone volume set to {val}%[/green]")
                    return {
                        "success": True,
                        "operation": "headphone_volume",
                        "value": val
                    }

            elif operation == "headphone_mix":
                if value is None:
                    return {"success": False, "error": "value required for headphone_mix operation"}

                val = max(0, min(100, int(value)))

                async with client:
                    result = await client.send_command(f"headphonemix {val}%")
                    if result["status"] != "success":
                        raise VDJError("Failed to set headphone mix")

                    console.print(f"[green]Headphone mix set to {val}%[/green]")
                    return {
                        "success": True,
                        "operation": "headphone_mix",
                        "value": val
                    }

            elif operation == "eq_reset":
                if deck_id is None:
                    return {"success": False, "error": "deck_id required for eq_reset operation"}

                async with client:
                    result = await client.send_command(f"deck {deck_id} eq reset")
                    if result["status"] != "success":
                        raise VDJError("Failed to reset EQ")

                    console.print(f"[green]Deck {deck_id} EQ reset[/green]")
                    return {
                        "success": True,
                        "operation": "eq_reset",
                        "deck_id": deck_id
                    }

            elif operation == "effect":
                if deck_id is None or effect_type is None:
                    return {"success": False, "error": "deck_id and effect_type required for effect operation"}

                # VDJ effect slots are 1-indexed (1, 2, 3)
                slot = max(1, min(3, effect_slot + 1))
                on_off = "on" if enable else "off"
                wd = max(0.0, min(100.0, wet_dry))

                # Command format: deck X effect Y 'name' [on/off] [wet_dry] [param1] [param2]
                cmd = f"deck {deck_id} effect {slot} '{effect_type}' {on_off} {wd}% {param1} {param2}"
                async with client:
                    result = await client.send_command(cmd)
                    if result["status"] != "success":
                        raise VDJError(f"Failed to set effect: {result.get('error', 'Unknown error')}")

                    console.print(f"[green]Deck {deck_id}: Slot {slot} effect '{effect_type}' {on_off} ({wd}% wet/dry)[/green]")
                    return {
                        "success": True,
                        "operation": "effect",
                        "deck_id": deck_id,
                        "effect_slot": effect_slot,
                        "effect_type": effect_type,
                        "enabled": enable,
                        "wet_dry": wd,
                        "param1": param1,
                        "param2": param2
                    }

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_mixer: {e}[/red]")
            return {"success": False, "error": str(e)}
