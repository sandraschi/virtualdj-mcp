"""
Recording Service for VirtualDJ-MCP

Handles recording and exporting of DJ mixes.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from rich.console import Console

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class RecordingStatus(Enum):
    """Status of the recording system"""
    STOPPED = "stopped"
    RECORDING = "recording"
    PAUSED = "paused"
    EXPORTING = "exporting"

class RecordingService:
    """
    Handles recording and exporting of DJ mixes.

    This service provides functionality to record audio output, manage recordings,
    and export them in various formats.
    """

    def __init__(self, output_dir: str = "recordings"):
        """
        Initialize the RecordingService.

        Args:
            output_dir: Base directory for storing recordings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.status = RecordingStatus.STOPPED
        self.current_recording: dict | None = None
        self.recordings: list[dict] = []
        self._recording_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

        # Load existing recordings metadata
        self._load_recordings()

    async def start_recording(self, name: str | None = None, format: str = "wav") -> dict[str, Any]:
        """
        Start a new recording session.

        Args:
            name: Optional name for the recording
            format: Output format (wav, mp3, ogg, flac)

        Returns:
            Dict with recording information
        """
        if self.status == RecordingStatus.RECORDING:
            return {
                "status": "error",
                "message": "A recording is already in progress"
            }

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name.replace(' ', '_')}" if name else f"recording_{timestamp}"
        filename = f"{filename}.{format}"
        filepath = self.output_dir / filename

        # Create recording metadata
        self.current_recording = {
            "id": str(hash(time.time())),
            "name": name or f"Recording {timestamp}",
            "filename": filename,
            "filepath": str(filepath),
            "format": format.lower(),
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "size": 0,
            "tags": {},
            "status": "recording"
        }

        # Start recording (implementation depends on VirtualDJ API)
        try:
            # TODO: Implement actual recording start with VirtualDJ API
            # await self._start_audio_capture(filepath, format)

            self.status = RecordingStatus.RECORDING
            self._stop_event.clear()

            # Start monitoring task
            self._recording_task = asyncio.create_task(self._monitor_recording())

            logger.info(f"Started recording: {filepath}")

            return {
                "status": "success",
                "recording_id": self.current_recording["id"],
                "filepath": str(filepath)
            }

        except Exception as e:
            logger.error(f"Failed to start recording: {e}", exc_info=True)
            self.status = RecordingStatus.STOPPED
            self.current_recording = None

            return {
                "status": "error",
                "message": f"Failed to start recording: {e!s}"
            }

    async def stop_recording(self) -> dict[str, Any]:
        """
        Stop the current recording.

        Returns:
            Dict with recording information
        """
        if self.status != RecordingStatus.RECORDING or not self.current_recording:
            return {
                "status": "error",
                "message": "No active recording to stop"
            }

        try:
            # Signal the monitoring task to stop
            self._stop_event.set()

            if self._recording_task and not self._recording_task.done():
                await self._recording_task

            # Update recording metadata
            end_time = time.time()
            self.current_recording["end_time"] = end_time
            self.current_recording["duration"] = end_time - self.current_recording["start_time"]

            # Get file size
            filepath = Path(self.current_recording["filepath"])
            if filepath.exists():
                self.current_recording["size"] = filepath.stat().st_size

            # Add to recordings list
            self.recordings.append(self.current_recording)

            # Save metadata
            self._save_recordings()

            logger.info(f"Stopped recording: {self.current_recording['name']}")

            # Return recording info
            result = self.current_recording.copy()
            self.current_recording = None
            self.status = RecordingStatus.STOPPED

            return {
                "status": "success",
                "recording": result
            }

        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to stop recording: {e!s}"
            }

    async def get_recording_status(self, recording_id: str | None = None) -> dict[str, Any]:
        """
        Get the status of the current or specified recording.

        Args:
            recording_id: Optional ID of a specific recording

        Returns:
            Dict with recording status
        """
        if recording_id:
            # Find a specific recording
            for rec in self.recordings:
                if rec["id"] == recording_id:
                    return {
                        "status": "success",
                        "recording": rec
                    }
            return {
                "status": "error",
                "message": f"Recording not found: {recording_id}"
            }

        # Return current recording status
        if self.status == RecordingStatus.RECORDING and self.current_recording:
            # Update duration for active recording
            self.current_recording["duration"] = time.time() - self.current_recording["start_time"]
            return {
                "status": "success",
                "recording": self.current_recording,
                "is_recording": True
            }

        return {
            "status": "success",
            "is_recording": False,
            "message": "No active recording"
        }

    async def export_mix_history(self, output_format: str = "json") -> dict[str, Any]:
        """
        Export the mix history in the specified format.

        Args:
            output_format: Output format (json, csv, txt)

        Returns:
            Dict with export information
        """
        try:
            output_format = output_format.lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mix_history_{timestamp}.{output_format}"
            filepath = self.output_dir / filename

            if output_format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.recordings, f, indent=2, default=str)

            # Add support for other formats here
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported export format: {output_format}",
                    "supported_formats": ["json"]  # Add more as implemented
                }

            return {
                "status": "success",
                "filepath": str(filepath),
                "recordings_exported": len(self.recordings)
            }

        except Exception as e:
            logger.error(f"Error exporting mix history: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to export mix history: {e!s}"
            }

    async def _monitor_recording(self):
        """Monitor the recording process and handle time limits/errors."""
        try:
            while not self._stop_event.is_set() and self.status == RecordingStatus.RECORDING:
                # Check for recording errors or time limits
                if self.current_recording:
                    # Update duration
                    self.current_recording["duration"] = time.time() - self.current_recording["start_time"]

                    # Check for maximum duration (e.g., 2 hours)
                    if self.current_recording["duration"] > 2 * 60 * 60:  # 2 hours
                        logger.warning("Maximum recording duration reached, stopping...")
                        await self.stop_recording()
                        break

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Recording monitoring task was cancelled")
        except Exception as e:
            logger.error(f"Error in recording monitor: {e}", exc_info=True)
            self.status = RecordingStatus.STOPPED
            self.current_recording = None

    def _load_recordings(self):
        """Load saved recordings metadata."""
        metadata_file = self.output_dir / "recordings_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, encoding='utf-8') as f:
                    self.recordings = json.load(f)
                logger.info(f"Loaded {len(self.recordings)} recordings from metadata")
            except Exception as e:
                logger.error(f"Error loading recordings metadata: {e}", exc_info=True)
                self.recordings = []

    def _save_recordings(self):
        """Save recordings metadata to disk."""
        if not self.recordings:
            return

        metadata_file = self.output_dir / "recordings_metadata.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.recordings, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving recordings metadata: {e}", exc_info=True)
