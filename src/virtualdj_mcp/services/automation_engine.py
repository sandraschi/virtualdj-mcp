"""
Automation Engine for VirtualDJ-MCP

Provides Auto-DJ functionality and intelligent track selection.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from secrets import SystemRandom

from rich.console import Console

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_secure_rng = SystemRandom()

# Initialize console for logging
console = Console()


class AutoDJStatus(Enum):
    """Status of the Auto-DJ system"""

    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"


@dataclass
class AutoDJPreferences:
    """User preferences for Auto-DJ behavior"""

    fade_time: int = 8  # seconds
    energy_matching: bool = True
    harmonic_mixing: bool = True
    genre_sticking: bool = True
    max_track_age: int = 60  # minutes
    min_energy_variation: float = 0.2


@dataclass
class AutoDJState:
    """Current state of the Auto-DJ system"""

    status: AutoDJStatus = AutoDJStatus.STOPPED
    current_genre: str | None = None
    current_energy: float = 0.5  # 0.0 to 1.0
    current_bpm: float = 120.0
    current_key: str | None = None
    next_track: dict | None = None
    history: list[dict] = field(default_factory=list)


class AutomationEngine:
    """
    Handles automated DJ functionality including track selection and mixing.

    This class provides intelligent track selection, automatic beatmatching,
    and smooth transitions between tracks.
    """

    def __init__(self, vdj_client, library_service, playlist_manager):
        """
        Initialize the Automation Engine.

        Args:
            vdj_client: Instance of VirtualDJClient for sending commands
            library_service: Instance of LibraryService for track lookup
            playlist_manager: Instance of PlaylistManager for playlist operations
        """
        self.vdj_client = vdj_client
        self.library = library_service
        self.playlist_manager = playlist_manager
        self.preferences = AutoDJPreferences()
        self.state = AutoDJState()
        self._stop_event = asyncio.Event()
        self._task = None

    async def start_auto_dj(self, duration_minutes: int = 60, genre_filter: str | None = None) -> bool:
        """
        Start the Auto-DJ system.

        Args:
            duration_minutes: Duration to run in minutes (0 for indefinite)
            genre_filter: Optional genre to filter tracks by

        Returns:
            bool: True if Auto-DJ started successfully
        """
        if self.state.status == AutoDJStatus.RUNNING:
            logger.warning("Auto-DJ is already running")
            return False

        self.state = AutoDJState(status=AutoDJStatus.RUNNING, current_genre=genre_filter)
        self._stop_event.clear()

        # Start the Auto-DJ task
        self._task = asyncio.create_task(self._auto_dj_loop(duration_minutes))
        logger.info(f"Auto-DJ started for {duration_minutes} minutes")
        return True

    async def stop_auto_dj(self) -> bool:
        """Stop the Auto-DJ system."""
        if self.state.status == AutoDJStatus.STOPPED:
            return False

        self.state.status = AutoDJStatus.STOPPED
        self._stop_event.set()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Auto-DJ stopped")
        return True

    async def get_auto_dj_status(self) -> dict:
        """
        Get the current status of the Auto-DJ system.

        Returns:
            Dict containing status information
        """
        return {
            "status": self.state.status.value,
            "current_genre": self.state.current_genre,
            "current_energy": self.state.current_energy,
            "current_bpm": self.state.current_bpm,
            "current_key": self.state.current_key,
            "next_track": self.state.next_track["title"] if self.state.next_track else None,
            "history": [t["title"] for t in self.state.history[-5:]],  # Last 5 tracks
        }

    def set_auto_dj_preferences(self, **prefs) -> bool:
        """
        Update Auto-DJ preferences.

        Args:
            **prefs: Preferences to update (fade_time, energy_matching, etc.)

        Returns:
            bool: True if preferences were updated successfully
        """
        for key, value in prefs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
                logger.info(f"Updated Auto-DJ preference: {key} = {value}")
        return True

    async def _auto_dj_loop(self, duration_minutes: int):
        """Main Auto-DJ event loop."""
        try:
            end_time = (
                asyncio.get_event_loop().time() + (duration_minutes * 60) if duration_minutes > 0 else float("inf")
            )

            while asyncio.get_event_loop().time() < end_time and not self._stop_event.is_set():
                if self.state.status != AutoDJStatus.RUNNING:
                    await asyncio.sleep(1)
                    continue

                # Get current track info
                current_track = await self._get_current_playing_track()

                # If we don't have a next track, select one
                if not self.state.next_track:
                    self.state.next_track = await self._select_next_track(current_track)

                # If we're close to the end of the current track, start transition
                if current_track and current_track.get("time_remaining", 0) < self.preferences.fade_time + 5:
                    await self._transition_to_next_track(current_track)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Auto-DJ loop was cancelled")
        except Exception as e:
            logger.error(f"Error in Auto-DJ loop: {e}", exc_info=True)
        finally:
            self.state.status = AutoDJStatus.STOPPED
            logger.info("Auto-DJ loop ended")

    async def _get_current_playing_track(self) -> dict | None:
        """Get information about the currently playing track."""
        # Implementation depends on VirtualDJ API
        # This is a placeholder - replace with actual implementation
        return {
            "id": "track123",
            "title": "Current Track",
            "artist": "Artist Name",
            "bpm": 128.0,
            "key": "Amin",
            "energy": 0.7,
            "duration": 240,  # seconds
            "time_elapsed": 180,  # seconds
            "time_remaining": 60,  # seconds
            "genre": "House",
            "deck_id": 1,
        }

    async def _select_next_track(self, current_track: dict | None = None) -> dict:
        """
        Select the next track to play based on current track and preferences.

        Args:
            current_track: Current track information or None if no track is playing

        Returns:
            Dict containing selected track information
        """
        # Build search filters based on preferences
        filters = {}

        if self.preferences.genre_sticking and self.state.current_genre:
            filters["genre"] = self.state.current_genre

        if self.preferences.energy_matching and current_track:
            target_energy = max(
                0.1,
                min(
                    0.9,
                    current_track.get("energy", 0.5)
                    + _secure_rng.uniform(
                        -self.preferences.min_energy_variation,
                        self.preferences.min_energy_variation,
                    ),
                ),
            )
            filters["energy"] = (target_energy - 0.1, target_energy + 0.1)

        if current_track and self.preferences.harmonic_mixing:
            # Get compatible keys based on current key
            compatible_keys = self._get_compatible_keys(current_track.get("key"))
            if compatible_keys:
                filters["key"] = compatible_keys

        # Search for tracks matching the filters
        matching_tracks = await self.library.search_tracks("", filters=filters)

        if not matching_tracks:
            # If no matches, relax the filters
            logger.warning("No matching tracks found, relaxing filters")
            matching_tracks = await self.library.search_tracks("")

        # Select a random track from matching tracks
        selected = _secure_rng.choice(matching_tracks)

        logger.info(f"Selected next track: {selected['title']} by {selected['artist']}")
        return selected

    async def _transition_to_next_track(self, current_track: dict):
        """
        Handle the transition from the current track to the next track.

        Args:
            current_track: Information about the currently playing track
        """
        if not self.state.next_track:
            logger.warning("No next track selected for transition")
            return

        self.state.status = AutoDJStatus.TRANSITIONING

        try:
            # Load the next track to the next available deck
            2 if current_track.get("deck_id", 1) == 1 else 1

            # Load the track (implementation depends on VirtualDJ API)
            # await self.vdj_client.load_track(next_deck, self.state.next_track["path"])

            # Start the next track at the right time
            # await self.vdj_client.play_deck(next_deck, sync_bpm=True)

            # Crossfade between tracks
            # await self._execute_crossfade(current_track["deck_id"], next_deck)

            # Update state
            self.state.history.append(current_track)
            if len(self.state.history) > 50:  # Keep history manageable
                self.state.history.pop(0)

            self.state.current_energy = self.state.next_track.get("energy", 0.5)
            self.state.current_bpm = self.state.next_track.get("bpm", 128.0)
            self.state.current_key = self.state.next_track.get("key")
            self.state.current_genre = self.state.next_track.get("genre")

            # Clear the next track so we'll select a new one
            self.state.next_track = None

        except Exception as e:
            logger.error(f"Error during transition: {e}", exc_info=True)
        finally:
            self.state.status = AutoDJStatus.RUNNING

    def _get_compatible_keys(self, key: str | None) -> list[str]:
        """
        Get a list of keys that are harmonically compatible with the given key.

        Args:
            key: Musical key (e.g., 'Amin', 'C#maj')

        Returns:
            List of compatible keys
        """
        if not key:
            return []

        # This is a simplified compatibility chart
        # In a real implementation, you'd want a more sophisticated system
        compatibility = {
            # Key: [Compatible keys]
            "Amin": ["C", "F", "G", "Dmin", "Emin"],
            "C": ["Amin", "F", "G", "Dmin", "Emin"],
            "G": ["Emin", "C", "D", "Amin", "Bmin"],
            "Emin": ["G", "C", "D", "Amin", "Bmin"],
            "F": ["Amin", "C", "Dmin", "Bb", "Gmin"],
            "Dmin": ["F", "Bb", "C", "Amin", "Gmin"],
            "D": ["Bmin", "G", "A", "Emin", "F#min"],
            "Bmin": ["D", "G", "A", "Emin", "F#min"],
        }

        return compatibility.get(key, [])

    async def _execute_crossfade(self, from_deck: int, to_deck: int):
        """
        Execute a smooth crossfade between two decks.

        Args:
            from_deck: Deck to fade out
            to_deck: Deck to fade in
        """
        steps = 10
        duration = self.preferences.fade_time
        step_duration = duration / steps

        for i in range(steps + 1):
            i / steps
            # await self.vdj_client.set_crossfader(position * 2 - 1)  # -1 to 1
            await asyncio.sleep(step_duration)

    async def suggest_next_track(self, current_track: dict, style: str = "similar") -> list[dict]:
        """
        Suggest tracks to play next based on the current track and style.

        Args:
            current_track: Information about the current track
            style: Suggestion style ('similar', 'energy_up', 'energy_down', 'genre_switch')

        Returns:
            List of suggested tracks
        """
        filters = {}

        if style == "similar":
            # Find similar tracks
            if current_track.get("genre"):
                filters["genre"] = current_track["genre"]
            if current_track.get("bpm"):
                filters["bpm"] = (current_track["bpm"] * 0.95, current_track["bpm"] * 1.05)

        elif style == "energy_up":
            # Find higher energy tracks
            if current_track.get("energy"):
                filters["energy"] = (current_track["energy"] + 0.1, 1.0)

        elif style == "energy_down":
            # Find lower energy tracks
            if current_track.get("energy"):
                filters["energy"] = (0.0, current_track["energy"] - 0.1)

        elif style == "genre_switch":
            # Find tracks in a different genre
            if current_track.get("genre"):
                filters["genre"] = {"$ne": current_track["genre"]}

        # Get matching tracks, excluding the current one
        tracks = await self.library.search_tracks("", filters=filters)
        tracks = [t for t in tracks if t["id"] != current_track.get("id")]

        # Sort by relevance (you could make this more sophisticated)
        if current_track.get("bpm"):
            tracks.sort(key=lambda x: abs(x.get("bpm", 0) - current_track["bpm"]))

        return tracks[:5]  # Return top 5 suggestions
