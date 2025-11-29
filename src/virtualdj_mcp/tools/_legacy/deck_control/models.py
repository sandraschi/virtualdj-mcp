"""
Pydantic models for deck control tools
"""

from typing import Optional

from pydantic import BaseModel, Field


class DeckStatus(BaseModel):
    """Current status of a DJ deck"""
    deck_id: int = Field(description="Deck number (1-8)")
    is_playing: bool = Field(description="Whether deck is currently playing")
    track_path: Optional[str] = Field(default=None, description="Path to currently loaded track")
    track_title: Optional[str] = Field(default=None, description="Track title")
    track_artist: Optional[str] = Field(default=None, description="Track artist")
    position: float = Field(default=0.0, description="Current position in seconds")
    duration: float = Field(default=0.0, description="Track duration in seconds")
    bpm: Optional[float] = Field(default=None, description="Beats per minute")
    key: Optional[str] = Field(default=None, description="Musical key")
    volume: int = Field(default=100, description="Deck volume (0-100)")
    pitch: float = Field(default=0.0, description="Pitch adjustment (-100 to +100)")




