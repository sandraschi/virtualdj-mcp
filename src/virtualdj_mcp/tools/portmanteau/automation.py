"""
VDJ Automation Portmanteau Tool

Consolidates Auto-DJ operations into a single interface.
Operations: start, stop, status, suggest, preferences
"""

from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

console = Console(file=__import__('sys').stderr)

_automation_engine = None


async def get_automation_engine():
    """Get initialized automation engine"""
    global _automation_engine
    if _automation_engine is None:
        from ...services.automation_engine import AutomationEngine
        _automation_engine = AutomationEngine()
    return _automation_engine


def setup_automation_portmanteau(mcp: FastMCP):
    """Register vdj_automation portmanteau tool."""

    @mcp.tool()
    async def vdj_automation(
        operation: Literal["start", "stop", "status", "suggest", "preferences"],
        duration_minutes: int = 60,
        genre_filter: str | None = None,
        fade_time: int | None = None,
        energy_matching: bool | None = None,
        harmonic_mixing: bool | None = None,
        genre_sticking: bool | None = None,
        min_energy_variation: float | None = None,
        suggestion_style: str = "similar",
        current_track_id: str | None = None,
        limit: int = 5
    ) -> dict[str, Any]:
        """
        Auto-DJ control for VirtualDJ.

        PORTMANTEAU PATTERN: Consolidates 5 Auto-DJ tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - start: Start Auto-DJ mode with optional configuration
        - stop: Stop Auto-DJ mode
        - status: Get current Auto-DJ status
        - suggest: Get track suggestions for next play
        - preferences: Update Auto-DJ preferences

        Args:
            operation: The Auto-DJ operation to perform
            duration_minutes: How long to run Auto-DJ (0 = indefinite)
            genre_filter: Filter tracks by genre
            fade_time: Crossfade duration in seconds
            energy_matching: Match energy between tracks
            harmonic_mixing: Mix in key (harmonic mixing)
            genre_sticking: Stay in same genre
            min_energy_variation: Minimum energy variation (0.0-1.0)
            suggestion_style: Suggestion type (similar, energy_up, energy_down, genre_switch)
            current_track_id: Track ID to base suggestions on
            limit: Max suggestions to return

        Returns:
            Dict with operation result

        Examples:
            vdj_automation("start", duration_minutes=120)
            vdj_automation("start", genre_filter="techno", harmonic_mixing=True)
            vdj_automation("stop")
            vdj_automation("status")
            vdj_automation("suggest", suggestion_style="energy_up", limit=5)
            vdj_automation("preferences", fade_time=8, harmonic_mixing=True)
        """
        try:
            engine = await get_automation_engine()

            if operation == "start":
                # Update preferences if provided
                prefs = {}
                if fade_time is not None:
                    prefs['fade_time'] = fade_time
                if energy_matching is not None:
                    prefs['energy_matching'] = energy_matching
                if harmonic_mixing is not None:
                    prefs['harmonic_mixing'] = harmonic_mixing
                if genre_sticking is not None:
                    prefs['genre_sticking'] = genre_sticking

                if prefs:
                    engine.set_auto_dj_preferences(**prefs)

                success = await engine.start_auto_dj(
                    duration_minutes=duration_minutes,
                    genre_filter=genre_filter
                )

                if not success:
                    return {"success": False, "error": "Failed to start Auto-DJ"}

                status = await engine.get_auto_dj_status()
                console.print(f"[green]Auto-DJ started for {duration_minutes} minutes[/green]")
                return {
                    "success": True,
                    "operation": "start",
                    "duration_minutes": duration_minutes,
                    "genre_filter": genre_filter,
                    **status
                }

            elif operation == "stop":
                success = await engine.stop_auto_dj()
                console.print("[green]Auto-DJ stopped[/green]")
                return {
                    "success": True,
                    "operation": "stop",
                    "was_running": success
                }

            elif operation == "status":
                status = await engine.get_auto_dj_status()
                return {
                    "success": True,
                    "operation": "status",
                    **status
                }

            elif operation == "suggest":
                if current_track_id:
                    current_track = await engine.library.get_track(current_track_id)
                    if not current_track:
                        return {"success": False, "error": "Track not found"}
                else:
                    current_track = await engine._get_current_playing_track()
                    if not current_track:
                        return {"success": False, "error": "No track currently playing"}

                suggestions = await engine.suggest_next_track(
                    current_track=current_track,
                    style=suggestion_style
                )
                suggestions = suggestions[:limit]

                return {
                    "success": True,
                    "operation": "suggest",
                    "style": suggestion_style,
                    "current_track": {
                        "id": current_track.get("id"),
                        "title": current_track.get("title"),
                        "artist": current_track.get("artist"),
                        "bpm": current_track.get("bpm"),
                        "key": current_track.get("key")
                    },
                    "suggestions": [
                        {
                            "id": t.get("id"),
                            "title": t.get("title"),
                            "artist": t.get("artist"),
                            "bpm": t.get("bpm"),
                            "key": t.get("key"),
                            "energy": t.get("energy"),
                            "compatibility_score": t.get("compatibility_score")
                        }
                        for t in suggestions
                    ]
                }

            elif operation == "preferences":
                prefs = {}
                if fade_time is not None:
                    prefs['fade_time'] = fade_time
                if energy_matching is not None:
                    prefs['energy_matching'] = energy_matching
                if harmonic_mixing is not None:
                    prefs['harmonic_mixing'] = harmonic_mixing
                if genre_sticking is not None:
                    prefs['genre_sticking'] = genre_sticking
                if min_energy_variation is not None:
                    prefs['min_energy_variation'] = min_energy_variation

                if not prefs:
                    return {"success": False, "error": "No preferences provided"}

                engine.set_auto_dj_preferences(**prefs)
                console.print("[green]Auto-DJ preferences updated[/green]")

                return {
                    "success": True,
                    "operation": "preferences",
                    "updated": prefs,
                    "current_preferences": {
                        "fade_time": engine.preferences.fade_time,
                        "energy_matching": engine.preferences.energy_matching,
                        "harmonic_mixing": engine.preferences.harmonic_mixing,
                        "genre_sticking": engine.preferences.genre_sticking,
                        "min_energy_variation": engine.preferences.min_energy_variation
                    }
                }

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_automation: {e}[/red]")
            return {"success": False, "error": str(e)}

