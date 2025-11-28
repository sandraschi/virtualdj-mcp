"""
VirtualDJ-MCP Configuration Management

Supports HTTP Network Control Plugin (recommended) and legacy CLI.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class VDJConfig(BaseModel):
    """Configuration for VirtualDJ-MCP server"""
    
    # VirtualDJ Application Settings
    virtualdj_path: str = Field(
        default="C:/Program Files/VirtualDJ/virtualdj.exe",
        description="Path to VirtualDJ executable"
    )
    
    # HTTP Network Control Plugin Settings
    http_host: str = Field(default="127.0.0.1", description="Network Control Plugin host")
    http_port: int = Field(default=80, description="Network Control Plugin port")
    http_password: Optional[str] = Field(default=None, description="Network Control Plugin password")
    http_timeout: float = Field(default=10.0, description="HTTP request timeout in seconds")
    
    # Legacy CLI Settings (deprecated - use HTTP instead)
    cli_enabled: bool = Field(default=False, description="Enable CLI command execution (deprecated)")
    cli_timeout: int = Field(default=30, description="CLI command timeout in seconds")
    
    # Library Settings
    music_library_path: Optional[str] = Field(
        default=None,
        description="Path to music library root directory"
    )
    auto_scan_library: bool = Field(default=True, description="Automatically scan library on startup")
    
    # Audio Settings
    default_volume: int = Field(default=75, description="Default deck volume (0-100)")
    auto_gain: bool = Field(default=True, description="Enable automatic gain control")
    crossfader_curve: str = Field(default="smooth", description="Crossfader curve type")
    
    # Automation Settings
    auto_sync_enabled: bool = Field(default=True, description="Enable automatic BPM sync")
    harmonic_mixing: bool = Field(default=True, description="Enable harmonic key mixing")
    auto_dj_fade_time: int = Field(default=5, description="Auto-DJ fade time in seconds")
    
    # Performance Settings
    max_decks: int = Field(default=4, description="Maximum number of decks to manage")
    update_interval: float = Field(default=0.5, description="Status update interval in seconds")
    
    # Recording Settings
    recording_path: str = Field(
        default="./recordings",
        description="Default path for mix recordings"
    )
    recording_format: str = Field(default="mp3", description="Default recording format")
    recording_quality: str = Field(default="320", description="Recording quality (kbps)")
    
    @classmethod
    def from_env(cls) -> "VDJConfig":
        """Create configuration from environment variables"""
        return cls(
            virtualdj_path=os.getenv("VDJ_PATH", cls.model_fields["virtualdj_path"].default),
            http_host=os.getenv("VDJ_HTTP_HOST", cls.model_fields["http_host"].default),
            http_port=int(os.getenv("VDJ_HTTP_PORT", cls.model_fields["http_port"].default)),
            http_password=os.getenv("VDJ_HTTP_PASSWORD"),
            http_timeout=float(os.getenv("VDJ_HTTP_TIMEOUT", cls.model_fields["http_timeout"].default)),
            music_library_path=os.getenv("VDJ_LIBRARY_PATH"),
            default_volume=int(os.getenv("VDJ_DEFAULT_VOLUME", cls.model_fields["default_volume"].default)),
            max_decks=int(os.getenv("VDJ_MAX_DECKS", cls.model_fields["max_decks"].default)),
            recording_path=os.getenv("VDJ_RECORDING_PATH", cls.model_fields["recording_path"].default),
        )
    
    def validate_paths(self) -> bool:
        """Validate that configured paths exist"""
        if not Path(self.virtualdj_path).exists():
            return False
        
        if self.music_library_path and not Path(self.music_library_path).exists():
            return False
            
        # Create recording path if it doesn't exist
        Path(self.recording_path).mkdir(parents=True, exist_ok=True)
        
        return True
    
