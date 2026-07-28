"""
Pydantic models for mixing tools
"""

from pydantic import BaseModel, Field


class MixerStatus(BaseModel):
    """Status of the DJ mixer"""

    crossfader_position: float = Field(description="Crossfader position (-100 to +100)")
    master_volume: int = Field(description="Master volume (0-100)")
    headphone_volume: int = Field(description="Headphone volume (0-100)")
    headphone_cue: str = Field(description="Headphone cue selection (deck1, deck2, master)")
