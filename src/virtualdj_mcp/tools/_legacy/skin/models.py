"""
Pydantic models for skin tools
"""

from typing import Optional

from pydantic import BaseModel, Field


class SkinInfo(BaseModel):
    """Information about the current VirtualDJ skin"""
    name: Optional[str] = Field(default=None, description="Current skin name")
    variation: Optional[str] = Field(default=None, description="Current skin variation")
    width: Optional[int] = Field(default=None, description="Skin width in pixels")
    height: Optional[int] = Field(default=None, description="Skin height in pixels")
    color: Optional[str] = Field(default=None, description="Skin accent color")
    deck_count: Optional[int] = Field(default=None, description="Number of decks in skin")


class PanelStatus(BaseModel):
    """Status of a skin panel"""
    panel_name: str = Field(description="Name of the panel")
    visible: bool = Field(description="Whether the panel is visible")


class SkinOperationResult(BaseModel):
    """Result of a skin operation"""
    success: bool = Field(description="Whether the operation succeeded")
    message: str = Field(description="Operation result message")
    skin_info: Optional[SkinInfo] = Field(default=None, description="Updated skin info if available")

