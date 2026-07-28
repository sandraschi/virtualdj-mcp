"""
VDJ Recording Portmanteau Tool

Consolidates recording operations into a single interface.
Operations: start, stop, status, list, export, delete
"""

import os
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from rich.console import Console

console = Console(file=__import__("sys").stderr)

_recording_service = None


async def get_recording_service():
    """Get initialized recording service"""
    global _recording_service
    if _recording_service is None:
        from ...config import VDJConfig
        from ...services.recording_service import RecordingService

        config = VDJConfig.from_env()
        output_dir = os.path.join(config.data_dir, "recordings")
        _recording_service = RecordingService(output_dir=output_dir)
    return _recording_service


def setup_recording_portmanteau(mcp: FastMCP):
    """Register vdj_recording portmanteau tool."""

    @mcp.tool()
    async def vdj_recording(
        operation: Literal["start", "stop", "status", "list", "export", "delete"],
        name: str | None = None,
        format: str = "wav",
        recording_id: str | None = None,
        output_format: str = "json",
        include_tracklist: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Recording control for VirtualDJ mixes.

        PORTMANTEAU PATTERN: Consolidates 6 recording tools into 1 unified interface.

        SUPPORTED OPERATIONS:
        - start: Start recording (optional name and format)
        - stop: Stop current recording
        - status: Get recording status (optional recording_id)
        - list: List all recordings
        - export: Export mix history
        - delete: Delete a recording (requires recording_id)

        Args:
            operation: The recording operation to perform
            name: Optional name for the recording
            format: Output format for recording (wav, mp3, ogg, flac)
            recording_id: ID of specific recording (for status/delete)
            output_format: Export format (json, csv, txt)
            include_tracklist: Include tracklist in export
            limit: Max recordings to return in list
            offset: Pagination offset for list

        Returns:
            Dict with operation result

        Examples:
            vdj_recording("start", name="Friday Night Mix", format="mp3")
            vdj_recording("stop")
            vdj_recording("status")
            vdj_recording("list", limit=20)
            vdj_recording("export", output_format="json")
            vdj_recording("delete", recording_id="rec_123")
        """
        try:
            service = await get_recording_service()

            if operation == "start":
                result = await service.start_recording(name, format)
                if result.get("status") == "error":
                    return {"success": False, "error": result.get("message")}

                console.print(f"[green]Recording started: {name or 'Untitled'}[/green]")
                return {"success": True, "operation": "start", **result}

            elif operation == "stop":
                result = await service.stop_recording()
                if result.get("status") == "error":
                    return {"success": False, "error": result.get("message")}

                console.print("[green]Recording stopped[/green]")
                return {"success": True, "operation": "stop", **result}

            elif operation == "status":
                result = await service.get_recording_status(recording_id)
                return {"success": True, "operation": "status", **result}

            elif operation == "list":
                recordings = service.recordings[offset : offset + limit]

                if service.status == "recording" and service.current_recording:
                    current = service.current_recording.copy()
                    current["is_current"] = True
                    recordings = [current, *recordings]

                return {
                    "success": True,
                    "operation": "list",
                    "recordings": recordings,
                    "total": len(service.recordings) + (1 if service.status == "recording" else 0),
                    "limit": limit,
                    "offset": offset,
                }

            elif operation == "export":
                result = await service.export_mix_history(output_format)

                if result.get("status") != "success":
                    return {"success": False, "error": result.get("message", "Export failed")}

                if include_tracklist and output_format == "json":
                    result["tracklist_included"] = False
                    result["message"] = "Tracklist export not yet implemented"

                console.print(f"[green]Mix history exported as {output_format}[/green]")
                return {"success": True, "operation": "export", **result}

            elif operation == "delete":
                if not recording_id:
                    return {"success": False, "error": "recording_id required for delete operation"}

                recording = None
                recording_idx = None
                for i, rec in enumerate(service.recordings):
                    if rec["id"] == recording_id:
                        recording = rec
                        recording_idx = i
                        break

                if not recording:
                    return {"success": False, "error": f"Recording not found: {recording_id}"}

                try:
                    filepath = Path(recording["filepath"])
                    if filepath.exists():
                        filepath.unlink()
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not delete file: {e}[/yellow]")

                service.recordings.pop(recording_idx)
                service._save_recordings()

                console.print(f"[green]Recording deleted: {recording_id}[/green]")
                return {"success": True, "operation": "delete", "recording_id": recording_id}

            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            console.print(f"[red]Error in vdj_recording: {e}[/red]")
            return {"success": False, "error": str(e)}
