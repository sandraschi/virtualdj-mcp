"""
VirtualDJ-MCP Configuration Management
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
    
    # API Settings
    rest_api_host: str = Field(default="localhost", description="VirtualDJ REST API host")
    rest_api_port: int = Field(default=8080, description="VirtualDJ REST API port")
    rest_api_enabled: bool = Field(default=True, description="Enable REST API communication")
    
    # CLI Settings
    cli_enabled: bool = Field(default=True, description="Enable CLI command execution")
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
            rest_api_host=os.getenv("VDJ_API_HOST", cls.model_fields["rest_api_host"].default),
            rest_api_port=int(os.getenv("VDJ_API_PORT", cls.model_fields["rest_api_port"].default)),
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
    
    @property
    def rest_api_url(self) -> str:
        """Get the full REST API URL"""
        return f"http://{self.rest_api_host}:{self.rest_api_port}"
