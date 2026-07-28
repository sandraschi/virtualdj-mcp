"""
Pydantic models for skin tools
"""

from pydantic import BaseModel, Field


class SkinInfo(BaseModel):
    """Information about the current VirtualDJ skin"""

    name: str | None = Field(default=None, description="Current skin name")
    variation: str | None = Field(default=None, description="Current skin variation")
    width: int | None = Field(default=None, description="Skin width in pixels")
    height: int | None = Field(default=None, description="Skin height in pixels")
    color: str | None = Field(default=None, description="Skin accent color")
    deck_count: int | None = Field(default=None, description="Number of decks in skin")


class PanelStatus(BaseModel):
    """Status of a skin panel"""

    panel_name: str = Field(description="Name of the panel")
    visible: bool = Field(description="Whether the panel is visible")


class SkinOperationResult(BaseModel):
    """Result of a skin operation"""

    success: bool = Field(description="Whether the operation succeeded")
    message: str = Field(description="Operation result message")
    skin_info: SkinInfo | None = Field(default=None, description="Updated skin info if available")
