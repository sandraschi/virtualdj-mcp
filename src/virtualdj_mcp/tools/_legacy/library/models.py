"""
Pydantic models for library tools
"""

from typing import Any

from pydantic import BaseModel, Field


class TrackInfo(BaseModel):
    """Information about a music track with extended metadata"""

    path: str = Field(..., description="File path to track")
    title: str = Field(..., description="Track title")
    artist: str = Field(..., description="Artist name")
    album: str | None = Field(None, description="Album name")
    genre: str | None = Field(None, description="Music genre")
    bpm: float | None = Field(None, description="Beats per minute")
    key: str | None = Field(None, description="Musical key")
    duration: float = Field(0.0, description="Duration in seconds")
    energy: float | None = Field(None, description="Energy level (0.0-1.0)")
    danceability: float | None = Field(None, description="Danceability score (0.0-1.0)")
    year: int | None = Field(None, description="Release year")
    bitrate: int | None = Field(None, description="Audio bitrate (kbps)")
    sample_rate: int | None = Field(None, description="Sample rate (Hz)")
    channels: int | None = Field(None, description="Number of audio channels")
    file_size: int | None = Field(None, description="File size in bytes")
    last_modified: float | None = Field(None, description="Last modified timestamp")
    play_count: int = Field(0, description="Number of times played")
    rating: int = Field(0, description="User rating (0-5)")
    tags: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {"datetime": lambda v: v.isoformat() if v else None}

    @classmethod
    def from_scanner_track(cls, track) -> "TrackInfo":
        """Create from LibraryScanner's TrackInfo"""
        return cls(
            path=track.file_path,
            title=track.title or track.file_path.split("/")[-1].split("\\")[-1].rsplit(".", 1)[0],
            artist=track.artist or "Unknown Artist",
            album=track.album,
            genre=track.genre,
            bpm=track.bpm,
            key=track.key,
            duration=track.duration,
            year=track.year,
            bitrate=track.bitrate,
            sample_rate=track.sample_rate,
            channels=track.channels,
            file_size=track.file_size,
            last_modified=track.last_modified,
            play_count=track.play_count,
            rating=track.rating,
            tags=track.tags,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        import json

        return json.loads(self.json())
