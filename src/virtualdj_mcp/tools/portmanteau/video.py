"""
VDJ Video Portmanteau Tool

Consolidates video operations into a single interface.
Operations: crossfader, transition, fx, text, output, master, karaoke, scratch, loop, tempo_sync, load
"""

from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

from ..shared.dependencies import get_vdj_client

console = Console(file=__import__("sys").stderr)


def setup_video_portmanteau(mcp: FastMCP):
    """Register vdj_video portmanteau tool."""

    @mcp.tool()
    async def vdj_video(
        operation: Literal[
            "crossfader",
            "transition",
            "fx",
            "text",
            "output",
            "master",
            "karaoke",
            "scratch",
            "loop",
            "tempo_sync",
            "load",
        ],
        deck_id: int | None = None,
        position: float | None = None,
        transition_type: str = "crossfade",
        duration: float = 1.0,
        effect: str | None = None,
        enabled: bool = True,
        intensity: int = 50,
        text: str | None = None,
        text_position: str = "bottom",
        font_size: int = 48,
        color: str = "white",
        fullscreen: bool = True,
        monitor: int = 2,
        mode: str = "auto",
        remove_vocals: bool = True,
        beats: float = 4,
        video_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Video control for VirtualDJ.

        VirtualDJ supports video mixing: MP4, AVI, MKV, MOV, WMV, FLV, WEBM.

        PORTMANTEAU PATTERN: Consolidates 11 video tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - crossfader: Set video crossfader position (-100 to +100)
        - transition: Set video transition effect and duration
        - fx: Apply video effects to a deck
        - text: Display text overlay on video output
        - output: Control external video output window
        - master: Set which deck appears on master output
        - karaoke: Enable karaoke mode on a deck
        - scratch: Enable video scratching (video follows audio scratch)
        - loop: Set video loop on a deck
        - tempo_sync: Sync video playback speed to audio tempo
        - load: Load a video file to a deck

        Args:
            operation: The video operation to perform
            deck_id: Deck number (1-8, required for most operations)
            position: Crossfader position (-100 to +100)
            transition_type: Transition type (crossfade, cut, fade, wipe_left, etc.)
            duration: Transition duration in seconds
            effect: Video effect name (negative, grayscale, sepia, blur, etc.)
            enabled: Enable/disable toggle
            intensity: Effect intensity (0-100)
            text: Text to display (for text operation)
            text_position: Text position (top, center, bottom)
            font_size: Font size in pixels
            color: Text color
            fullscreen: Enable fullscreen output
            monitor: Monitor number for output
            mode: Master output mode (auto, deck, split, pip)
            remove_vocals: Remove vocals in karaoke mode
            beats: Number of beats for video loop
            video_path: Path to video file

        Returns:
            Dict with operation result

        Examples:
            vdj_video("crossfader", position=0)        # Center blend
            vdj_video("transition", transition_type="cube", duration=2.0)
            vdj_video("fx", deck_id=1, effect="sepia", intensity=75)
            vdj_video("text", text="DJ Sandra", text_position="bottom")
            vdj_video("output", fullscreen=True, monitor=2)
            vdj_video("master", mode="auto")
            vdj_video("karaoke", deck_id=1, enabled=True)
            vdj_video("loop", deck_id=1, beats=4)
            vdj_video("load", deck_id=1, video_path="C:/Videos/clip.mp4")
        """
        try:
            client = await get_vdj_client()

            if operation == "crossfader":
                if position is None:
                    return {"success": False, "error": "position required for crossfader operation"}

                pos = max(-100, min(100, position))
                vdj_pos = int((pos + 100) / 2)

                async with client:
                    await client.send_command(f"video_crossfader {vdj_pos}%")
                    console.print(f"[green]Video crossfader set to {pos}[/green]")
                    return {"success": True, "operation": "crossfader", "position": pos}

            elif operation == "transition":
                transitions = {
                    "crossfade": "crossfade",
                    "cut": "cut",
                    "fade": "fade",
                    "wipe_left": "wipe_left",
                    "wipe_right": "wipe_right",
                    "wipe_up": "wipe_up",
                    "wipe_down": "wipe_down",
                    "zoom": "zoom",
                    "spin": "spin",
                    "cube": "cube",
                    "flip": "flip",
                    "slide_left": "slide_left",
                    "slide_right": "slide_right",
                }
                vdj_transition = transitions.get(transition_type.lower(), "crossfade")
                dur = max(0.1, min(10.0, duration))

                async with client:
                    await client.send_command(f"video_transition '{vdj_transition}'")
                    await client.send_command(f"video_transition_time {int(dur * 1000)}ms")
                    console.print(f"[green]Video transition: {vdj_transition} ({dur}s)[/green]")
                    return {"success": True, "operation": "transition", "transition": vdj_transition, "duration": dur}

            elif operation == "fx":
                if not deck_id or not effect:
                    return {"success": False, "error": "deck_id and effect required for fx operation"}

                async with client:
                    if enabled:
                        await client.send_command(f"deck {deck_id} video_fx '{effect}'")
                        await client.send_command(f"deck {deck_id} video_fx_slider {intensity}%")
                    else:
                        await client.send_command(f"deck {deck_id} video_fx 'none'")

                    console.print(
                        f"[green]Deck {deck_id}: Video FX '{effect}' {'enabled' if enabled else 'disabled'}[/green]"
                    )
                    return {
                        "success": True,
                        "operation": "fx",
                        "deck_id": deck_id,
                        "effect": effect,
                        "enabled": enabled,
                        "intensity": intensity,
                    }

            elif operation == "text":
                if not text:
                    return {"success": False, "error": "text required for text operation"}

                safe_text = text.replace("'", "\\'").replace('"', '\\"')
                position_map = {"top": "top", "center": "middle", "bottom": "bottom"}
                vdj_position = position_map.get(text_position.lower(), "bottom")

                async with client:
                    await client.send_command(f"video_text '{safe_text}'")
                    await client.send_command(f"video_text_position '{vdj_position}'")
                    await client.send_command(f"video_text_size {font_size}")
                    await client.send_command(f"video_text_color '{color}'")

                    if duration > 0:
                        await client.send_command(f"video_text_duration {int(duration * 1000)}ms")

                    console.print(f"[green]Video text: '{text}' at {text_position}[/green]")
                    return {"success": True, "operation": "text", "text": text, "position": text_position}

            elif operation == "output":
                async with client:
                    if enabled:
                        await client.send_command("video_window 'show'")
                        if fullscreen:
                            await client.send_command(f"video_window 'fullscreen' {monitor}")
                    else:
                        await client.send_command("video_window 'hide'")

                    console.print(f"[green]Video output: {'enabled' if enabled else 'disabled'}[/green]")
                    return {
                        "success": True,
                        "operation": "output",
                        "enabled": enabled,
                        "fullscreen": fullscreen,
                        "monitor": monitor,
                    }

            elif operation == "master":
                async with client:
                    if mode == "auto":
                        await client.send_command("video_master 'auto'")
                    elif mode == "split":
                        await client.send_command("video_master 'split'")
                    elif mode == "pip":
                        await client.send_command("video_master 'pip'")
                    elif mode == "deck" and deck_id:
                        await client.send_command(f"video_master 'deck' {deck_id}")

                    console.print(f"[green]Video master: {mode}[/green]")
                    return {"success": True, "operation": "master", "mode": mode, "deck_id": deck_id}

            elif operation == "karaoke":
                if not deck_id:
                    return {"success": False, "error": "deck_id required for karaoke operation"}

                async with client:
                    if enabled:
                        await client.send_command(f"deck {deck_id} karaoke on")
                        if remove_vocals:
                            await client.send_command(f"deck {deck_id} stem_kill 'vocal'")
                    else:
                        await client.send_command(f"deck {deck_id} karaoke off")
                        await client.send_command(f"deck {deck_id} stem_unkill 'vocal'")

                    console.print(f"[green]Deck {deck_id}: Karaoke {'ON' if enabled else 'OFF'}[/green]")
                    return {"success": True, "operation": "karaoke", "deck_id": deck_id, "enabled": enabled}

            elif operation == "scratch":
                if not deck_id:
                    return {"success": False, "error": "deck_id required for scratch operation"}

                async with client:
                    state = "on" if enabled else "off"
                    await client.send_command(f"deck {deck_id} video_scratch {state}")
                    console.print(f"[green]Deck {deck_id}: Video scratch {'ON' if enabled else 'OFF'}[/green]")
                    return {"success": True, "operation": "scratch", "deck_id": deck_id, "enabled": enabled}

            elif operation == "loop":
                if not deck_id:
                    return {"success": False, "error": "deck_id required for loop operation"}

                async with client:
                    if enabled:
                        await client.send_command(f"deck {deck_id} video_loop {beats}")
                    else:
                        await client.send_command(f"deck {deck_id} video_loop_exit")

                    console.print(
                        f"[green]Deck {deck_id}: Video loop {'set to ' + str(beats) + ' beats' if enabled else 'exited'}[/green]"
                    )
                    return {
                        "success": True,
                        "operation": "loop",
                        "deck_id": deck_id,
                        "beats": beats if enabled else None,
                    }

            elif operation == "tempo_sync":
                if not deck_id:
                    return {"success": False, "error": "deck_id required for tempo_sync operation"}

                async with client:
                    state = "on" if enabled else "off"
                    await client.send_command(f"deck {deck_id} video_tempo_sync {state}")
                    console.print(f"[green]Deck {deck_id}: Video tempo sync {'ON' if enabled else 'OFF'}[/green]")
                    return {"success": True, "operation": "tempo_sync", "deck_id": deck_id, "enabled": enabled}

            elif operation == "load":
                if not deck_id or not video_path:
                    return {"success": False, "error": "deck_id and video_path required for load operation"}

                async with client:
                    await client.load_track(deck_id, video_path)
                    console.print(f"[green]Video loaded to Deck {deck_id}[/green]")
                    return {"success": True, "operation": "load", "deck_id": deck_id, "video_path": video_path}

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_video: {e}[/red]")
            return {"success": False, "error": str(e)}
