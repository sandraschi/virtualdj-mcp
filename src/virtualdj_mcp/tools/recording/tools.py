"""
Recording Tools for VirtualDJ-MCP

This module provides MCP tools for recording and exporting DJ mixes.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from rich.console import Console

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# Global reference to the recording service
_recording_service = None


async def get_recording_service():
    """Get initialized recording service"""
    global _recording_service
    if _recording_service is None:
        import os

        from ...config import VDJConfig
        from ...services.recording_service import RecordingService
        config = VDJConfig.from_env()
        output_dir = os.path.join(config.data_dir, "recordings")
        _recording_service = RecordingService(output_dir=output_dir)
    return _recording_service


def setup_recording_tools(mcp: FastMCP):
    """
    Set up recording-related MCP tools.

    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    async def start_recording(
        name: Optional[str] = None, 
        format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Start recording the current mix.
        
        Args:
            name: Optional name for the recording
            format: Output format (wav, mp3, ogg, flac)
            
        Returns:
            Dict with recording information
        """
        try:
            service = await get_recording_service()
            return await service.start_recording(name, format)
        except Exception as e:
            logger.error(f"Error starting recording: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to start recording: {str(e)}"
            }
    
    @mcp.tool()
    async def stop_recording() -> Dict[str, Any]:
        """
        Stop the current recording.
        
        Returns:
            Dict with recording information
        """
        try:
            service = await get_recording_service()
            return await service.stop_recording()
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to stop recording: {str(e)}"
            }
    
    @mcp.tool()
    async def get_recording_status(recording_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the status of the current or specified recording.
        
        Args:
            recording_id: Optional ID of a specific recording
            
        Returns:
            Dict with recording status
        """
        try:
            service = await get_recording_service()
            return await service.get_recording_status(recording_id)
        except Exception as e:
            logger.error(f"Error getting recording status: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to get recording status: {str(e)}"
            }
    
    @mcp.tool()
    async def list_recordings(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List all available recordings.
        
        Args:
            limit: Maximum number of recordings to return
            offset: Offset for pagination
            
        Returns:
            Dict with list of recordings and metadata
        """
        try:
            service = await get_recording_service()
            # Get all recordings except the current one (if any)
            recordings = service.recordings[offset:offset + limit]

            # If there's a current recording, include it at the beginning
            if service.status == "recording" and service.current_recording:
                current = service.current_recording.copy()
                current["is_current"] = True
                recordings = [current] + recordings

            return {
                "status": "success",
                "recordings": recordings,
                "total": len(service.recordings) + (1 if service.status == "recording" else 0),
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error listing recordings: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to list recordings: {str(e)}"
            }
    
    @mcp.tool()
    async def export_mix_history(
        output_format: str = "json",
        include_tracklist: bool = True
    ) -> Dict[str, Any]:
        """
        Export the mix history in the specified format.
        
        Args:
            output_format: Output format (json, csv, txt)
            include_tracklist: Whether to include tracklist in export
            
        Returns:
            Dict with export information
        """
        try:
            service = await get_recording_service()
            # First export the basic mix history
            result = await service.export_mix_history(output_format)
            
            if result["status"] != "success":
                return result
            
            # If tracklist should be included, add it to the export
            if include_tracklist and output_format == "json":
                # This would be enhanced with actual tracklist data from VirtualDJ
                # For now, we'll just add a placeholder
                result["tracklist_included"] = False
                result["message"] = "Tracklist export not yet implemented"
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting mix history: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to export mix history: {str(e)}"
            }
    
    @mcp.tool()
    async def delete_recording(recording_id: str) -> Dict[str, Any]:
        """
        Delete a recording.
        
        Args:
            recording_id: ID of the recording to delete
            
        Returns:
            Dict with status information
        """
        try:
            service = await get_recording_service()
            # Find the recording
            recording = None
            for i, rec in enumerate(service.recordings):
                if rec["id"] == recording_id:
                    recording = rec
                    break

            if not recording:
                return {
                    "status": "error",
                    "message": f"Recording not found: {recording_id}"
                }

            # Delete the file
            try:
                filepath = Path(recording["filepath"])
                if filepath.exists():
                    filepath.unlink()
            except Exception as e:
                logger.warning(f"Could not delete recording file: {e}")

            # Remove from recordings list
            service.recordings.pop(i)
            service._save_recordings()
            
            return {
                "status": "success",
                "message": f"Recording deleted: {recording_id}",
                "recording_id": recording_id
            }
            
        except Exception as e:
            logger.error(f"Error deleting recording: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to delete recording: {str(e)}"
            }
