"""
Auto-DJ Tools for VirtualDJ-MCP

This module provides MCP tools for Auto-DJ functionality.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from rich.console import Console

from ...services.automation_engine import AutomationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# Global reference to the automation engine
_automation_engine = None


async def get_automation_engine() -> AutomationEngine:
    """Get initialized automation engine"""
    global _automation_engine
    if _automation_engine is None:
        _automation_engine = AutomationEngine()
    return _automation_engine


def setup_auto_dj_tools(mcp: FastMCP):
    """
    Set up Auto-DJ related MCP tools.

    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    async def auto_dj_mode(
        duration_minutes: int = 60, 
        genre_filter: Optional[str] = None,
        fade_time: Optional[int] = None,
        energy_matching: Optional[bool] = None,
        harmonic_mixing: Optional[bool] = None,
        genre_sticking: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Start or configure the Auto-DJ mode.
        
        Args:
            duration_minutes: How long to run Auto-DJ (0 for indefinite)
            genre_filter: Optional genre to filter tracks by
            fade_time: Crossfade duration in seconds (optional)
            energy_matching: Whether to match energy between tracks (optional)
            harmonic_mixing: Whether to mix in key (optional)
            genre_sticking: Whether to stay in the same genre (optional)
            
        Returns:
            Dict with status information
        """
        try:
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
                engine = await get_automation_engine()
                engine.set_auto_dj_preferences(**prefs)

            # Start Auto-DJ
            engine = await get_automation_engine()
            success = await engine.start_auto_dj(
                duration_minutes=duration_minutes,
                genre_filter=genre_filter
            )
            
            if not success:
                return {"status": "error", "message": "Failed to start Auto-DJ"}
                
            return {
                "status": "success",
                "message": f"Auto-DJ started for {duration_minutes} minutes",
                **await engine.get_auto_dj_status()
            }
            
        except Exception as e:
            logger.error(f"Error in auto_dj_mode: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    async def stop_auto_dj() -> Dict[str, Any]:
        """
        Stop the Auto-DJ mode.
        
        Returns:
            Dict with status information
        """
        try:
            engine = await get_automation_engine()
            success = await engine.stop_auto_dj()
            return {
                "status": "success" if success else "already_stopped",
                "message": "Auto-DJ stopped"
            }
        except Exception as e:
            logger.error(f"Error stopping Auto-DJ: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    async def get_auto_dj_status() -> Dict[str, Any]:
        """
        Get the current status of the Auto-DJ system.
        
        Returns:
            Dict with status information
        """
        try:
            engine = await get_automation_engine()
            return {
                "status": "success",
                **await engine.get_auto_dj_status()
            }
        except Exception as e:
            logger.error(f"Error getting Auto-DJ status: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    async def suggest_next_track(
        style: str = "similar",
        current_track_id: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get track suggestions based on current playback or specified track.
        
        Args:
            style: Suggestion style ('similar', 'energy_up', 'energy_down', 'genre_switch')
            current_track_id: Optional track ID to base suggestions on
            limit: Maximum number of suggestions to return
            
        Returns:
            Dict with suggested tracks and metadata
        """
        try:
            engine = await get_automation_engine()
            if current_track_id:
                # Get track by ID
                current_track = await engine.library.get_track(current_track_id)
                if not current_track:
                    return {"status": "error", "message": "Track not found"}
            else:
                # Get currently playing track
                current_track = await engine._get_current_playing_track()
                if not current_track:
                    return {"status": "error", "message": "No track currently playing"}

            # Get suggestions
            suggestions = await engine.suggest_next_track(
                current_track=current_track,
                style=style
            )
            
            # Limit results
            suggestions = suggestions[:limit]
            
            return {
                "status": "success",
                "current_track": {
                    "id": current_track.get("id"),
                    "title": current_track.get("title"),
                    "artist": current_track.get("artist"),
                    "bpm": current_track.get("bpm"),
                    "key": current_track.get("key"),
                    "energy": current_track.get("energy")
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
                ],
                "suggestion_style": style
            }
            
        except Exception as e:
            logger.error(f"Error getting track suggestions: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    async def set_auto_dj_preferences(
        fade_time: Optional[int] = None,
        energy_matching: Optional[bool] = None,
        harmonic_mixing: Optional[bool] = None,
        genre_sticking: Optional[bool] = None,
        min_energy_variation: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update Auto-DJ preferences.
        
        Args:
            fade_time: Crossfade duration in seconds
            energy_matching: Whether to match energy between tracks
            harmonic_mixing: Whether to mix in key
            genre_sticking: Whether to stay in the same genre
            min_energy_variation: Minimum energy variation (0.0-1.0)
            
        Returns:
            Dict with status and updated preferences
        """
        try:
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
                return {
                    "status": "error",
                    "message": "No preferences provided"
                }

            engine = await get_automation_engine()
            engine.set_auto_dj_preferences(**prefs)

            # Get current status to return updated preferences
            await engine.get_auto_dj_status()

            return {
                "status": "success",
                "message": "Auto-DJ preferences updated",
                "preferences": {
                    "fade_time": engine.preferences.fade_time,
                    "energy_matching": engine.preferences.energy_matching,
                    "harmonic_mixing": engine.preferences.harmonic_mixing,
                    "genre_sticking": engine.preferences.genre_sticking,
                    "min_energy_variation": engine.preferences.min_energy_variation
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating Auto-DJ preferences: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
