"""
Playlist Manager for VirtualDJ-MCP

This module provides functionality to manage playlists, including creation,
modification, and querying of playlist data.
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PlaylistTrack:
    """Represents a track within a playlist with additional metadata."""

    track_id: str
    position: int
    added_at: float = field(default_factory=lambda: datetime.now().timestamp())
    played: bool = False
    play_count: int = 0
    last_played: float | None = None
    rating: int = 0  # 0-5, 0 = unrated
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "track_id": self.track_id,
            "position": self.position,
            "added_at": self.added_at,
            "played": self.played,
            "play_count": self.play_count,
            "last_played": self.last_played,
            "rating": self.rating,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlaylistTrack":
        """Create from dictionary."""
        return cls(
            track_id=data["track_id"],
            position=data.get("position", 0),
            added_at=data.get("added_at", datetime.now().timestamp()),
            played=data.get("played", False),
            play_count=data.get("play_count", 0),
            last_played=data.get("last_played"),
            rating=data.get("rating", 0),
            tags=data.get("tags", {}),
        )


@dataclass
class Playlist:
    """Represents a playlist with tracks and metadata."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    tracks: list[PlaylistTrack] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    is_public: bool = False
    owner_id: str | None = None
    cover_art: str | None = None

    def __post_init__(self):
        # Ensure tracks are properly sorted by position
        self.sort_tracks()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tracks": [track.to_dict() for track in self.tracks],
            "tags": list(self.tags),
            "is_public": self.is_public,
            "owner_id": self.owner_id,
            "cover_art": self.cover_art,
            "track_count": len(self.tracks),
            "duration": self.duration,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Playlist":
        """Create from dictionary."""
        playlist = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.now().timestamp()),
            updated_at=data.get("updated_at", datetime.now().timestamp()),
            tags=set(data.get("tags", [])),
            is_public=data.get("is_public", False),
            owner_id=data.get("owner_id"),
            cover_art=data.get("cover_art"),
        )

        # Add tracks
        for track_data in data.get("tracks", []):
            playlist.tracks.append(PlaylistTrack.from_dict(track_data))

        return playlist

    @property
    def duration(self) -> float:
        """Calculate total duration of all tracks in the playlist (in seconds)."""
        # This is a placeholder - in a real implementation, you would sum the durations
        # of all tracks from your database or track metadata
        return sum(180 for _ in self.tracks)  # Assuming 3 minutes per track as default

    def sort_tracks(self) -> None:
        """Sort tracks by their position."""
        self.tracks.sort(key=lambda x: x.position)

    def update_position(self, track_id: str, new_position: int) -> bool:
        """
        Update the position of a track in the playlist.

        Args:
            track_id: ID of the track to move
            new_position: New position (0-based)

        Returns:
            bool: True if the track was found and moved, False otherwise
        """
        # Find the track
        track = next((t for t in self.tracks if t.track_id == track_id), None)
        if not track:
            return False

        # Remove the track
        self.tracks = [t for t in self.tracks if t.track_id != track_id]

        # Update position of other tracks
        for t in self.tracks:
            if t.position >= new_position:
                t.position += 1

        # Reinsert the track at the new position
        track.position = new_position
        self.tracks.append(track)
        self.sort_tracks()

        # Update timestamp
        self.updated_at = datetime.now().timestamp()
        return True

    def add_track(self, track_id: str, position: int | None = None) -> bool:
        """
        Add a track to the playlist.

        Args:
            track_id: ID of the track to add
            position: Position to insert the track (None = append to end)

        Returns:
            bool: True if the track was added, False if it already exists
        """
        # Check if track already exists in playlist
        if any(t.track_id == track_id for t in self.tracks):
            return False

        # Determine position
        if position is None:
            position = len(self.tracks)

        # Create new playlist track
        playlist_track = PlaylistTrack(track_id=track_id, position=position)

        # Update positions of other tracks if needed
        if position < len(self.tracks):
            for track in self.tracks:
                if track.position >= position:
                    track.position += 1

        # Add the track
        self.tracks.append(playlist_track)
        self.sort_tracks()

        # Update timestamp
        self.updated_at = datetime.now().timestamp()
        return True

    def remove_track(self, track_id: str) -> bool:
        """
        Remove a track from the playlist.

        Args:
            track_id: ID of the track to remove

        Returns:
            bool: True if the track was removed, False if not found
        """
        # Find the track
        track = next((t for t in self.tracks if t.track_id == track_id), None)
        if not track:
            return False

        # Remove the track and update positions
        position = track.position
        self.tracks = [t for t in self.tracks if t.track_id != track_id]

        # Update positions of remaining tracks
        for t in self.tracks:
            if t.position > position:
                t.position -= 1

        # Update timestamp
        self.updated_at = datetime.now().timestamp()
        return True

    def get_track_ids(self) -> list[str]:
        """Get a list of all track IDs in the playlist."""
        return [t.track_id for t in sorted(self.tracks, key=lambda x: x.position)]

    def get_track_position(self, track_id: str) -> int | None:
        """Get the position of a track in the playlist."""
        track = next((t for t in self.tracks if t.track_id == track_id), None)
        return track.position if track else None


class PlaylistManager:
    """Manages playlists for the VirtualDJ-MCP system."""

    def __init__(self, storage_path: str | None = None):
        """
        Initialize the playlist manager.

        Args:
            storage_path: Path to store playlist data (default: ~/.virtualdj-mcp/playlists)
        """
        # Set up storage path
        if storage_path is None:
            storage_path = os.path.expanduser("~/.virtualdj-mcp/playlists")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache of playlists
        self._playlists: dict[str, Playlist] = {}

        logger.info(f"Initialized PlaylistManager with storage path: {self.storage_path}")

    async def load_playlists(self) -> None:
        """Load all playlists from disk."""
        try:
            self._playlists = {}

            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        playlist = Playlist.from_dict(data)
                        self._playlists[playlist.id] = playlist
                    logger.debug(f"Loaded playlist: {playlist.name} ({playlist.id})")
                except Exception as e:
                    logger.error(f"Error loading playlist from {file_path}: {e!s}")

            logger.info(f"Loaded {len(self._playlists)} playlists from disk")

        except Exception as e:
            logger.error(f"Error loading playlists: {e!s}")
            raise

    async def save_playlist(self, playlist: Playlist) -> None:
        """
        Save a playlist to disk.

        Args:
            playlist: Playlist to save
        """
        try:
            # Update timestamp
            playlist.updated_at = datetime.now().timestamp()

            # Convert to dict
            data = playlist.to_dict()

            # Save to file
            file_path = self.storage_path / f"{playlist.id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Update cache
            self._playlists[playlist.id] = playlist

            logger.debug(f"Saved playlist: {playlist.name} ({playlist.id})")

        except Exception as e:
            logger.error(f"Error saving playlist {playlist.id}: {e!s}")
            raise

    async def create_playlist(
        self, name: str, description: str = "", is_public: bool = False, owner_id: str | None = None
    ) -> Playlist:
        """
        Create a new playlist.

        Args:
            name: Name of the playlist
            description: Optional description
            is_public: Whether the playlist is public
            owner_id: ID of the playlist owner (user)

        Returns:
            The created Playlist object
        """
        playlist = Playlist(name=name, description=description, is_public=is_public, owner_id=owner_id)

        await self.save_playlist(playlist)
        logger.info(f"Created new playlist: {name} ({playlist.id})")
        return playlist

    async def get_playlist(self, playlist_id: str) -> Playlist | None:
        """
        Get a playlist by ID.

        Args:
            playlist_id: ID of the playlist to retrieve

        Returns:
            The Playlist object, or None if not found
        """
        # Check cache first
        if playlist_id in self._playlists:
            return self._playlists[playlist_id]

        # Try to load from disk
        file_path = self.storage_path / f"{playlist_id}.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    playlist = Playlist.from_dict(data)
                    self._playlists[playlist_id] = playlist
                    return playlist
            except Exception as e:
                logger.error(f"Error loading playlist {playlist_id}: {e!s}")

        return None

    async def get_all_playlists(self) -> list[Playlist]:
        """
        Get all playlists.

        Returns:
            List of all Playlist objects
        """
        # Ensure we've loaded all playlists
        if not self._playlists:
            await self.load_playlists()

        return list(self._playlists.values())

    async def update_playlist(self, playlist_id: str, **updates) -> Playlist | None:
        """
        Update playlist metadata.

        Args:
            playlist_id: ID of the playlist to update
            **updates: Fields to update (name, description, is_public, etc.)

        Returns:
            The updated Playlist, or None if not found
        """
        playlist = await self.get_playlist(playlist_id)
        if not playlist:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(playlist, key):
                setattr(playlist, key, value)

        # Save changes
        await self.save_playlist(playlist)
        logger.info(f"Updated playlist: {playlist.name} ({playlist_id})")
        return playlist

    async def delete_playlist(self, playlist_id: str) -> bool:
        """
        Delete a playlist.

        Args:
            playlist_id: ID of the playlist to delete

        Returns:
            bool: True if deleted, False if not found
        """
        # Try to get the playlist first to log its name
        playlist = await self.get_playlist(playlist_id)
        if not playlist:
            return False

        # Delete from disk
        file_path = self.storage_path / f"{playlist_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.error(f"Error deleting playlist file {file_path}: {e!s}")
            return False

        # Remove from cache
        if playlist_id in self._playlists:
            del self._playlists[playlist_id]

        logger.info(f"Deleted playlist: {playlist.name} ({playlist_id})")
        return True

    async def add_track_to_playlist(self, playlist_id: str, track_id: str, position: int | None = None) -> bool:
        """
        Add a track to a playlist.

        Args:
            playlist_id: ID of the playlist
            track_id: ID of the track to add
            position: Position to insert the track (None = append to end)

        Returns:
            bool: True if added, False if already exists or playlist not found
        """
        playlist = await self.get_playlist(playlist_id)
        if not playlist:
            return False

        # Add the track
        result = playlist.add_track(track_id, position)
        if result:
            await self.save_playlist(playlist)
            logger.debug(f"Added track {track_id} to playlist {playlist.name}")

        return result

    async def remove_track_from_playlist(self, playlist_id: str, track_id: str) -> bool:
        """
        Remove a track from a playlist.

        Args:
            playlist_id: ID of the playlist
            track_id: ID of the track to remove

        Returns:
            bool: True if removed, False if not found or playlist not found
        """
        playlist = await self.get_playlist(playlist_id)
        if not playlist:
            return False

        # Remove the track
        result = playlist.remove_track(track_id)
        if result:
            await self.save_playlist(playlist)
            logger.debug(f"Removed track {track_id} from playlist {playlist.name}")

        return result

    async def reorder_track_in_playlist(self, playlist_id: str, track_id: str, new_position: int) -> bool:
        """
        Reorder a track within a playlist.

        Args:
            playlist_id: ID of the playlist
            track_id: ID of the track to move
            new_position: New position (0-based)

        Returns:
            bool: True if moved, False if track or playlist not found
        """
        playlist = await self.get_playlist(playlist_id)
        if not playlist:
            return False

        # Update the position
        result = playlist.update_position(track_id, new_position)
        if result:
            await self.save_playlist(playlist)
            logger.debug(f"Moved track {track_id} to position {new_position} in playlist {playlist.name}")

        return result

    async def search_playlists(self, query: str, limit: int = 50, owner_id: str | None = None) -> list[Playlist]:
        """
        Search for playlists by name or description.

        Args:
            query: Search query
            limit: Maximum number of results to return
            owner_id: Optional filter by owner ID

        Returns:
            List of matching Playlist objects
        """
        # Ensure we've loaded all playlists
        if not self._playlists:
            await self.load_playlists()

        query = query.lower()
        results = []

        for playlist in self._playlists.values():
            # Skip if owner filter is set and doesn't match
            if owner_id is not None and playlist.owner_id != owner_id:
                continue

            # Check if query matches name or description
            if (
                query in playlist.name.lower()
                or query in playlist.description.lower()
                or any(query in tag.lower() for tag in playlist.tags)
            ):
                results.append(playlist)

            # Limit results
            if len(results) >= limit:
                break

        return results


# Example usage
async def example_usage():
    """Example of how to use the PlaylistManager class."""
    import shutil
    import tempfile

    # Create a temporary directory for testing
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Initialize the playlist manager
        manager = PlaylistManager(storage_path=temp_dir)

        # Create some playlists
        playlist1 = await manager.create_playlist(
            name="My Favorite Tracks",
            description="A collection of my favorite tracks",
            is_public=True,
            owner_id="user123",
        )

        playlist2 = await manager.create_playlist(
            name="Workout Mix", description="High-energy tracks for working out", is_public=False, owner_id="user123"
        )

        # Add some tracks to the first playlist
        track_ids = [f"track_{i}" for i in range(1, 6)]
        for i, track_id in enumerate(track_ids):
            await manager.add_track_to_playlist(playlist1.id, track_id, i)

        # Print all playlists
        print("All playlists:")
        for playlist in await manager.get_all_playlists():
            print(f"- {playlist.name} ({len(playlist.tracks)} tracks)")

        # Search for playlists
        print("\nSearch results for 'workout':")
        results = await manager.search_playlists("workout")
        for playlist in results:
            print(f"- {playlist.name}")

        # Reorder tracks in the first playlist
        await manager.reorder_track_in_playlist(playlist1.id, "track_3", 0)

        # Get the updated playlist
        updated = await manager.get_playlist(playlist1.id)
        print(f"\nUpdated track order in {updated.name}:")
        for i, track in enumerate(updated.tracks):
            print(f"{i + 1}. {track.track_id}")

        # Clean up
        await manager.delete_playlist(playlist1.id)
        await manager.delete_playlist(playlist2.id)

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
