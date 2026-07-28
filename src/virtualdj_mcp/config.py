"""
VirtualDJ-MCP Configuration Management

Supports HTTP Network Control Plugin (recommended) and legacy CLI.
"""

import os
from pathlib import Path

from pydantic import BaseModel, Field


class VDJConfig(BaseModel):
    """Configuration for VirtualDJ-MCP server"""

    # VirtualDJ Application Settings
    virtualdj_path: str = Field(
        default="C:/Program Files/VirtualDJ/virtualdj.exe", description="Path to VirtualDJ executable"
    )

    # HTTP Network Control Plugin Settings
    http_host: str = Field(default="127.0.0.1", description="Network Control Plugin host")
    http_port: int = Field(default=80, description="Network Control Plugin port")
    http_password: str | None = Field(default=None, description="Network Control Plugin password")
    http_timeout: float = Field(default=10.0, description="HTTP request timeout in seconds")

    # OSC (OS2V) — must match VirtualDJ exactly; from_env() requires VDJ_OSC_PORT (see from_env)
    osc_port: int = Field(
        default=40100,
        ge=1,
        le=65535,
        description="OSC (OS2V) UDP port — must match VirtualDJ Settings → OSC; wrong port breaks control",
    )

    # Legacy CLI Settings (deprecated - use HTTP instead)
    cli_enabled: bool = Field(default=False, description="Enable CLI command execution (deprecated)")
    cli_timeout: int = Field(default=30, description="CLI command timeout in seconds")

    # Library Settings
    music_library_path: str | None = Field(default=None, description="Path to music library root directory")
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
    recording_path: str = Field(default="./recordings", description="Default path for mix recordings")
    recording_format: str = Field(default="mp3", description="Default recording format")
    recording_quality: str = Field(default="320", description="Recording quality (kbps)")

    @classmethod
    def from_env(cls) -> "VDJConfig":
        """Create configuration from environment variables.

        OSC (OS2V) is not optional for correct control: ``VDJ_OSC_PORT`` must match the UDP port
        in VirtualDJ (Settings → OSC). If unset here we default the process env to **40100** (VirtualDJ
        factory default); if VirtualDJ uses another port, you **must** set ``VDJ_OSC_PORT`` or OSC
        commands will not reach the app.
        """
        raw_osc = os.getenv("VDJ_OSC_PORT")
        if raw_osc is None or not str(raw_osc).strip():
            # Factory default; still must match VirtualDJ — set VDJ_OSC_PORT if yours differs.
            raw_osc = "40100"
            os.environ["VDJ_OSC_PORT"] = raw_osc
        try:
            osc_port = int(str(raw_osc).strip(), 10)
        except ValueError as e:
            raise ValueError("VDJ_OSC_PORT must be an integer UDP port in the range 1–65535.") from e

        return cls(
            virtualdj_path=os.getenv("VDJ_PATH", cls.model_fields["virtualdj_path"].default),
            http_host=os.getenv("VDJ_HTTP_HOST", cls.model_fields["http_host"].default),
            http_port=int(os.getenv("VDJ_HTTP_PORT", cls.model_fields["http_port"].default)),
            http_password=os.getenv("VDJ_HTTP_PASSWORD"),
            http_timeout=float(os.getenv("VDJ_HTTP_TIMEOUT", cls.model_fields["http_timeout"].default)),
            osc_port=osc_port,
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
