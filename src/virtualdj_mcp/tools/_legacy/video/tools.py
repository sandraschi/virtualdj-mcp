"""
Video Tools for VirtualDJ-MCP

VirtualDJ supports full video mixing capabilities:
- Video file playback (MP4, AVI, MKV, etc.)
- Video transitions and crossfading
- Video effects (FX)
- Text overlays and titles
- Karaoke support
- External video output to projectors/screens

Supported formats: AVI, MPEG, WMV, VOB, MOV, DIVX, MP4, M4V, MKV, FLV, WEBM
"""

from fastmcp import FastMCP


def setup_video_tools(mcp: FastMCP):
    """Register all video-related tools with the MCP server."""

    @mcp.tool()
    async def video_crossfader(position: float) -> dict:
        """
        Set the video crossfader position.

        The video crossfader controls the blend between video on deck A and deck B,
        independent of the audio crossfader.

        Args:
            position: Crossfader position (-100 to +100)
                     -100 = Full deck A (left)
                       0  = 50/50 blend
                     +100 = Full deck B (right)

        Returns:
            Dict with video crossfader status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        # Clamp position
        position = max(-100, min(100, position))

        # VDJ uses 0-100 for video_crossfader where 50 is center
        vdj_pos = int((position + 100) / 2)

        await vdj.send_command(f"video_crossfader {vdj_pos}%")

        return {
            "success": True,
            "video_crossfader": position,
            "vdj_value": vdj_pos
        }

    @mcp.tool()
    async def video_transition(
        transition_type: str = "crossfade",
        duration: float = 1.0
    ) -> dict:
        """
        Set the video transition effect between decks.

        Args:
            transition_type: Type of transition. Options:
                - "crossfade" (default) - Smooth blend
                - "cut" - Hard cut
                - "fade" - Fade through black
                - "wipe_left" / "wipe_right" - Wipe transitions
                - "wipe_up" / "wipe_down" - Vertical wipes
                - "zoom" - Zoom transition
                - "spin" - Spinning transition
                - "cube" - 3D cube rotation
                - "flip" - Page flip
                - "slide_left" / "slide_right" - Slide transitions
            duration: Transition duration in seconds (0.1 to 10.0)

        Returns:
            Dict with transition settings
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        # Map friendly names to VDJ transition names
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
            "slide_right": "slide_right"
        }

        vdj_transition = transitions.get(transition_type.lower(), "crossfade")
        duration = max(0.1, min(10.0, duration))

        await vdj.send_command(f"video_transition '{vdj_transition}'")
        await vdj.send_command(f"video_transition_time {int(duration * 1000)}ms")

        return {
            "success": True,
            "transition": vdj_transition,
            "duration_seconds": duration
        }

    @mcp.tool()
    async def video_fx(
        deck_id: int,
        effect: str,
        enabled: bool = True,
        intensity: int = 50
    ) -> dict:
        """
        Apply video effects to a deck.

        Args:
            deck_id: Deck number (1-8)
            effect: Video effect name. Options:
                - "none" - Remove all effects
                - "negative" - Color inversion
                - "grayscale" / "bw" - Black and white
                - "sepia" - Vintage sepia tone
                - "blur" - Gaussian blur
                - "sharpen" - Edge enhancement
                - "mirror" - Horizontal mirror
                - "flip" - Vertical flip
                - "kaleidoscope" - Kaleidoscope pattern
                - "strobe" - Strobe flash effect
                - "color_shift" - Hue rotation
                - "pixelate" - Pixelation
                - "edge" - Edge detection
                - "emboss" - Embossed look
                - "vhs" - VHS retro effect
                - "glitch" - Digital glitch
            enabled: Whether to enable or disable the effect
            intensity: Effect intensity (0-100)

        Returns:
            Dict with effect status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        effects = {
            "none": "video_fx 'none'",
            "negative": "video_fx 'negative'",
            "grayscale": "video_fx 'grayscale'",
            "bw": "video_fx 'grayscale'",
            "sepia": "video_fx 'sepia'",
            "blur": "video_fx 'blur'",
            "sharpen": "video_fx 'sharpen'",
            "mirror": "video_fx 'mirror'",
            "flip": "video_fx 'flip'",
            "kaleidoscope": "video_fx 'kaleidoscope'",
            "strobe": "video_fx 'strobe'",
            "color_shift": "video_fx 'colorize'",
            "pixelate": "video_fx 'pixelate'",
            "edge": "video_fx 'edge'",
            "emboss": "video_fx 'emboss'",
            "vhs": "video_fx 'vhs'",
            "glitch": "video_fx 'glitch'"
        }

        fx_cmd = effects.get(effect.lower(), f"video_fx '{effect}'")

        if enabled:
            await vdj.send_command(f"deck {deck_id} {fx_cmd}")
            await vdj.send_command(f"deck {deck_id} video_fx_slider {intensity}%")
        else:
            await vdj.send_command(f"deck {deck_id} video_fx 'none'")

        return {
            "success": True,
            "deck": deck_id,
            "effect": effect,
            "enabled": enabled,
            "intensity": intensity
        }

    @mcp.tool()
    async def video_text_overlay(
        text: str,
        position: str = "bottom",
        duration: float = 5.0,
        font_size: int = 48,
        color: str = "white"
    ) -> dict:
        """
        Display text overlay on the video output.

        Perfect for:
        - Track titles
        - DJ name
        - Announcements
        - Karaoke lyrics
        - Event branding

        Args:
            text: Text to display
            position: Position on screen ("top", "center", "bottom")
            duration: How long to display in seconds (0 for permanent)
            font_size: Font size in pixels (12-200)
            color: Text color ("white", "black", "red", "blue", "yellow", etc.)

        Returns:
            Dict with overlay status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        # Escape quotes in text
        safe_text = text.replace("'", "\\'").replace('"', '\\"')

        position_map = {"top": "top", "center": "middle", "bottom": "bottom"}
        vdj_position = position_map.get(position.lower(), "bottom")

        await vdj.send_command(f"video_text '{safe_text}'")
        await vdj.send_command(f"video_text_position '{vdj_position}'")
        await vdj.send_command(f"video_text_size {font_size}")
        await vdj.send_command(f"video_text_color '{color}'")

        if duration > 0:
            await vdj.send_command(f"video_text_duration {int(duration * 1000)}ms")

        return {
            "success": True,
            "text": text,
            "position": position,
            "duration": duration if duration > 0 else "permanent",
            "font_size": font_size,
            "color": color
        }

    @mcp.tool()
    async def video_output(
        enabled: bool = True,
        fullscreen: bool = True,
        monitor: int = 2
    ) -> dict:
        """
        Control the external video output window.

        VirtualDJ can output video to a second monitor, projector, or LED wall.
        Requires dual-monitor setup (Extended Desktop mode).

        Args:
            enabled: Whether to show or hide the video output window
            fullscreen: Whether to display in fullscreen mode
            monitor: Which monitor to display on (1 = primary, 2 = secondary, etc.)

        Returns:
            Dict with video output status

        Note:
            VirtualDJ Pro license required to remove watermark from output.
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        if enabled:
            await vdj.send_command("video_window 'show'")
            if fullscreen:
                await vdj.send_command(f"video_window 'fullscreen' {monitor}")
        else:
            await vdj.send_command("video_window 'hide'")

        return {
            "success": True,
            "enabled": enabled,
            "fullscreen": fullscreen,
            "monitor": monitor
        }

    @mcp.tool()
    async def video_master_output(
        deck_id: int | None = None,
        mode: str = "auto"
    ) -> dict:
        """
        Set which deck's video appears on the master output.

        Args:
            deck_id: Specific deck to show (1-8), or None for auto
            mode: Output mode:
                - "auto" - Follow audio crossfader
                - "deck" - Fixed to specified deck
                - "split" - Show both decks side by side
                - "pip" - Picture-in-picture mode

        Returns:
            Dict with master output settings
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        if mode == "auto":
            await vdj.send_command("video_master 'auto'")
        elif mode == "split":
            await vdj.send_command("video_master 'split'")
        elif mode == "pip":
            await vdj.send_command("video_master 'pip'")
        elif mode == "deck" and deck_id:
            await vdj.send_command(f"video_master 'deck' {deck_id}")

        return {
            "success": True,
            "mode": mode,
            "deck": deck_id if mode == "deck" else "auto"
        }

    @mcp.tool()
    async def karaoke_mode(
        deck_id: int,
        enabled: bool = True,
        remove_vocals: bool = True
    ) -> dict:
        """
        Enable karaoke mode on a deck.

        Karaoke mode can:
        - Display scrolling lyrics (if embedded in file)
        - Remove/reduce vocals using stem separation
        - Show karaoke-style highlighting

        Args:
            deck_id: Deck number (1-8)
            enabled: Enable or disable karaoke mode
            remove_vocals: Also remove vocals using stem separation

        Returns:
            Dict with karaoke mode status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        if enabled:
            await vdj.send_command(f"deck {deck_id} karaoke on")
            if remove_vocals:
                await vdj.send_command(f"deck {deck_id} stem_kill 'vocal'")
        else:
            await vdj.send_command(f"deck {deck_id} karaoke off")
            await vdj.send_command(f"deck {deck_id} stem_unkill 'vocal'")

        return {
            "success": True,
            "deck": deck_id,
            "karaoke_mode": enabled,
            "vocals_removed": remove_vocals if enabled else False
        }

    @mcp.tool()
    async def video_scratch(
        deck_id: int,
        enabled: bool = True
    ) -> dict:
        """
        Enable video scratching - video follows audio scratch movements.

        When enabled, scratching the audio will also scratch the video,
        creating a DJ-style video scratch effect.

        Args:
            deck_id: Deck number (1-8)
            enabled: Enable or disable video scratch sync

        Returns:
            Dict with video scratch status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        state = "on" if enabled else "off"
        await vdj.send_command(f"deck {deck_id} video_scratch {state}")

        return {
            "success": True,
            "deck": deck_id,
            "video_scratch": enabled
        }

    @mcp.tool()
    async def video_loop(
        deck_id: int,
        beats: float = 4,
        enabled: bool = True
    ) -> dict:
        """
        Set a video loop on a deck.

        The video will loop for the specified number of beats,
        synced with the audio loop if one is active.

        Args:
            deck_id: Deck number (1-8)
            beats: Number of beats to loop (0.25, 0.5, 1, 2, 4, 8, 16, 32)
            enabled: Enable or disable the video loop

        Returns:
            Dict with video loop status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        if enabled:
            await vdj.send_command(f"deck {deck_id} video_loop {beats}")
        else:
            await vdj.send_command(f"deck {deck_id} video_loop_exit")

        return {
            "success": True,
            "deck": deck_id,
            "video_loop": enabled,
            "beats": beats if enabled else None
        }

    @mcp.tool()
    async def video_tempo_sync(
        deck_id: int,
        enabled: bool = True
    ) -> dict:
        """
        Sync video playback speed to audio tempo.

        When enabled, changing the audio tempo (pitch/BPM) will also
        adjust the video playback speed to match.

        Args:
            deck_id: Deck number (1-8)
            enabled: Enable or disable tempo sync

        Returns:
            Dict with tempo sync status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        state = "on" if enabled else "off"
        await vdj.send_command(f"deck {deck_id} video_tempo_sync {state}")

        return {
            "success": True,
            "deck": deck_id,
            "video_tempo_sync": enabled
        }

    @mcp.tool()
    async def load_video_to_deck(
        deck_id: int,
        video_path: str
    ) -> dict:
        """
        Load a video file to a deck.

        Supported formats: AVI, MPEG, WMV, VOB, MOV, DIVX, MP4, M4V, MKV, FLV, WEBM

        Args:
            deck_id: Deck number (1-8)
            video_path: Path to video file

        Returns:
            Dict with load status
        """
        from ..shared.dependencies import get_vdj_client

        vdj = await get_vdj_client()

        # Use the standard load_track command - VDJ handles video files automatically
        await vdj.load_track(deck_id, video_path)

        return {
            "success": True,
            "deck": deck_id,
            "video_path": video_path,
            "message": f"Video loaded to Deck {deck_id}"
        }

