"""
Mixer Controller for VirtualDJ-MCP

Provides advanced mixing controls including EQ, effects, and crossfader management.
"""

import logging
from dataclasses import dataclass
from enum import Enum

from rich.console import Console

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize console for logging
console = Console()


class EQBand(Enum):
    """EQ frequency bands"""

    LOW = "low"
    MID = "mid"
    HIGH = "high"


class EffectType(Enum):
    """Available effect types"""

    FILTER = "filter"
    FLANGER = "flanger"
    ECHO = "echo"
    REVERB = "reverb"
    GATE = "gate"
    PHASER = "phaser"
    ROLL = "roll"
    TRANSFORM = "transform"


@dataclass
class EQSettings:
    """EQ settings for a single deck or master"""

    low: float = 0.0  # -24dB to +12dB
    mid: float = 0.0  # -24dB to +12dB
    high: float = 0.0  # -24dB to +12dB
    kill_low: bool = False
    kill_mid: bool = False
    kill_high: bool = False

    def to_dict(self) -> dict[str, float | bool]:
        """Convert to dictionary for serialization"""
        return {
            "low": self.low,
            "mid": self.mid,
            "high": self.high,
            "kill_low": self.kill_low,
            "kill_mid": self.kill_mid,
            "kill_high": self.kill_high,
        }


@dataclass
class EffectSettings:
    """Effect settings for a single effect"""

    effect_type: EffectType
    enabled: bool = False
    wet_dry: float = 50.0  # 0-100%
    param1: float = 0.0  # Effect-specific parameter 1
    param2: float = 0.0  # Effect-specific parameter 2

    def to_dict(self) -> dict[str, str | float | bool]:
        """Convert to dictionary for serialization"""
        return {
            "effect_type": self.effect_type.value,
            "enabled": self.enabled,
            "wet_dry": self.wet_dry,
            "param1": self.param1,
            "param2": self.param2,
        }


class MixerController:
    """
    Controller for advanced mixing features including EQ, effects, and crossfader.

    This class provides a high-level interface for controlling the VirtualDJ mixer
    with support for per-deck EQ, effects, and crossfader management.
    """

    def __init__(self, vdj_client):
        """Initialize the mixer controller.

        Args:
            vdj_client: Instance of VirtualDJClient for sending commands
        """
        self.vdj_client = vdj_client
        self.eq_settings: dict[int, EQSettings] = {}  # deck_id -> EQSettings
        self.effects: dict[int, list[EffectSettings]] = {}  # deck_id -> List[EffectSettings]
        self.crossfader_curve: float = 0.0  # -1.0 to 1.0
        self.master_volume: float = 0.8  # 0.0 to 1.0
        self.headphone_volume: float = 0.7  # 0.0 to 1.0
        self.headphone_mix: float = 0.5  # 0.0 (master) to 1.0 (cue)

        # Initialize default EQ settings for all decks (1-8)
        for deck_id in range(1, 9):
            self.eq_settings[deck_id] = EQSettings()
            self.effects[deck_id] = [
                EffectSettings(EffectType.FILTER),
                EffectSettings(EffectType.FLANGER),
                EffectSettings(EffectType.ECHO),
            ]

    async def set_eq_band(self, deck_id: int, band: EQBand, value: float) -> bool:
        """Set an EQ band for a specific deck.

        Args:
            deck_id: Deck number (1-8)
            band: EQ band to adjust (low, mid, high)
            value: Gain value in dB (-24 to +12)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clamp value to valid range
            value = max(-24.0, min(12.0, value))

            # Update local state
            if deck_id in self.eq_settings:
                if band == EQBand.LOW:
                    self.eq_settings[deck_id].low = value
                elif band == EQBand.MID:
                    self.eq_settings[deck_id].mid = value
                elif band == EQBand.HIGH:
                    self.eq_settings[deck_id].high = value

                # Send command to VirtualDJ
                cmd = f"deck {deck_id} eq {band.value} {value}"
                await self.vdj_client.send_command(cmd)

                logger.info(f"Set deck {deck_id} {band.value} EQ to {value}dB")
                return True

            return False

        except Exception as e:
            logger.error(f"Error setting EQ band: {e}")
            return False

    async def kill_eq_band(self, deck_id: int, band: EQBand, kill: bool = True) -> bool:
        """Kill or restore an EQ band for a specific deck.

        Args:
            deck_id: Deck number (1-8)
            band: EQ band to kill/restore
            kill: True to kill, False to restore

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if deck_id in self.eq_settings:
                if band == EQBand.LOW:
                    self.eq_settings[deck_id].kill_low = kill
                elif band == EQBand.MID:
                    self.eq_settings[deck_id].kill_mid = kill
                elif band == EQBand.HIGH:
                    self.eq_settings[deck_id].kill_high = kill

                # Send command to VirtualDJ
                cmd = f"deck {deck_id} eq {band.value} {'kill' if kill else 'restore'}"
                await self.vdj_client.send_command(cmd)

                logger.info(f"{'Killed' if kill else 'Restored'} {band.value} EQ on deck {deck_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error {'killing' if kill else 'restoring'} EQ band: {e}")
            return False

    async def reset_eq(self, deck_id: int) -> bool:
        """Reset all EQ bands for a specific deck to 0dB.

        Args:
            deck_id: Deck number (1-8)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if deck_id in self.eq_settings:
                # Reset local state
                self.eq_settings[deck_id] = EQSettings()

                # Send command to VirtualDJ
                cmd = f"deck {deck_id} eq reset"
                await self.vdj_client.send_command(cmd)

                logger.info(f"Reset EQ for deck {deck_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error resetting EQ: {e}")
            return False

    async def set_effect(
        self,
        deck_id: int,
        effect_slot: int,
        effect_type: EffectType,
        enabled: bool = True,
        wet_dry: float = 50.0,
        param1: float = 0.0,
        param2: float = 0.0,
    ) -> bool:
        """Configure an effect for a specific deck.

        Args:
            deck_id: Deck number (1-8)
            effect_slot: Effect slot (0-2)
            effect_type: Type of effect to apply
            enabled: Whether the effect is active
            wet_dry: Wet/dry mix (0-100%)
            param1: Effect-specific parameter 1
            param2: Effect-specific parameter 2

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if deck_id in self.effects and 0 <= effect_slot < len(self.effects[deck_id]):
                # Update local state
                self.effects[deck_id][effect_slot] = EffectSettings(
                    effect_type=effect_type,
                    enabled=enabled,
                    wet_dry=max(0.0, min(100.0, wet_dry)),
                    param1=param1,
                    param2=param2,
                )

                # Send command to VirtualDJ
                cmd = (
                    f"deck {deck_id} effect {effect_slot + 1} "
                    f"{effect_type.value} {'on' if enabled else 'off'} "
                    f"{wet_dry} {param1} {param2}"
                )
                await self.vdj_client.send_command(cmd)

                logger.info(f"Set effect {effect_type.value} on deck {deck_id}, slot {effect_slot}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error setting effect: {e}")
            return False

    async def set_crossfader(self, position: float) -> bool:
        """Set the crossfader position.

        Args:
            position: Crossfader position (-1.0 to 1.0)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clamp position to valid range
            position = max(-1.0, min(1.0, position))
            self.crossfader_curve = position

            # Convert to VirtualDJ format (0-100%)
            vdj_position = int((position + 1.0) * 50.0)

            # Send command to VirtualDJ
            cmd = f"crossfader {vdj_position}"
            await self.vdj_client.send_command(cmd)

            logger.debug(f"Set crossfader to {position:.2f}")
            return True

        except Exception as e:
            logger.error(f"Error setting crossfader: {e}")
            return False

    async def set_master_volume(self, volume: float) -> bool:
        """Set the master volume.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clamp volume to valid range
            volume = max(0.0, min(1.0, volume))
            self.master_volume = volume

            # Convert to VirtualDJ format (0-100%)
            vdj_volume = int(volume * 100.0)

            # Send command to VirtualDJ
            cmd = f"mastervolume {vdj_volume}"
            await self.vdj_client.send_command(cmd)

            logger.debug(f"Set master volume to {volume:.2f}")
            return True

        except Exception as e:
            logger.error(f"Error setting master volume: {e}")
            return False

    async def set_headphone_volume(self, volume: float) -> bool:
        """Set the headphone volume.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clamp volume to valid range
            volume = max(0.0, min(1.0, volume))
            self.headphone_volume = volume

            # Convert to VirtualDJ format (0-100%)
            vdj_volume = int(volume * 100.0)

            # Send command to VirtualDJ
            cmd = f"headphone {vdj_volume}"
            await self.vdj_client.send_command(cmd)

            logger.debug(f"Set headphone volume to {volume:.2f}")
            return True

        except Exception as e:
            logger.error(f"Error setting headphone volume: {e}")
            return False

    async def set_headphone_mix(self, mix: float) -> bool:
        """Set the headphone mix between master and cue.

        Args:
            mix: Mix level (0.0 = master, 1.0 = cue)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clamp mix to valid range
            mix = max(0.0, min(1.0, mix))
            self.headphone_mix = mix

            # Convert to VirtualDJ format (0-100%)
            vdj_mix = int(mix * 100.0)

            # Send command to VirtualDJ
            cmd = f"headphonemix {vdj_mix}"
            await self.vdj_client.send_command(cmd)

            logger.debug(f"Set headphone mix to {mix:.2f}")
            return True

        except Exception as e:
            logger.error(f"Error setting headphone mix: {e}")
            return False

    def get_mixer_state(self, deck_id: int) -> dict:
        """Get the current mixer state for a specific deck.

        Args:
            deck_id: Deck number (1-8)

        Returns:
            Dict containing the mixer state
        """
        eq_settings = self.eq_settings.get(deck_id, EQSettings())
        effect_states = [effect.to_dict() for effect in self.effects.get(deck_id, [])]

        return {
            "deck_id": deck_id,
            "eq": eq_settings.to_dict(),
            "effects": effect_states,
            "crossfader": self.crossfader_curve,
            "master_volume": self.master_volume,
            "headphone_volume": self.headphone_volume,
            "headphone_mix": self.headphone_mix,
        }
