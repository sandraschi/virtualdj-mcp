"""
Test script for VirtualDJ-MCP MixerController

This script provides interactive testing of the MixerController class.
Run with: python -m tests.test_mixer_controller
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.virtualdj_mcp.config import VDJConfig
from src.virtualdj_mcp.core.vdj_client import VirtualDJClient
from src.virtualdj_mcp.mixer_controller import EffectType, EQBand, MixerController


async def test_eq_controls(controller: MixerController, deck_id: int = 1):
    """Test EQ controls for a deck"""
    print(f"\n=== Testing EQ Controls (Deck {deck_id}) ===")

    # Reset EQ first
    print("\nResetting EQ...")
    result = await controller.reset_eq(deck_id)
    print(f"Reset EQ: {result}")

    # Test setting EQ bands
    print("\nSetting EQ bands...")
    for band in [EQBand.LOW, EQBand.MID, EQBand.HIGH]:
        result = await controller.set_eq_band(deck_id, band, 6.0)  # Boost by 6dB
        print(f"Set {band.name} to +6dB: {result}")

    # Test killing EQ bands
    print("\nKilling EQ bands...")
    for band in [EQBand.LOW, EQBand.MID, EQBand.HIGH]:
        result = await controller.kill_eq_band(deck_id, band, kill=True)
        print(f"Killed {band.name}: {result}")

    # Get final status
    status = controller.get_mixer_state(deck_id)
    print("\nFinal EQ status:", status["eq"])

async def test_effects(controller: MixerController, deck_id: int = 1):
    """Test effect controls for a deck"""
    print(f"\n=== Testing Effect Controls (Deck {deck_id}) ===")

    # Test setting different effects
    effects = [
        (EffectType.FILTER, 75.0, 0.5, 0.0),  # Filter with wet/dry 75%
        (EffectType.FLANGER, 50.0, 0.3, 0.7),  # Flanger with parameters
        (EffectType.ECHO, 60.0, 0.4, 0.0)      # Echo effect
    ]

    for i, (effect_type, wet_dry, p1, p2) in enumerate(effects):
        print(f"\nSetting {effect_type.name} effect...")
        result = await controller.set_effect(
            deck_id=deck_id,
            effect_slot=i,
            effect_type=effect_type,
            enabled=True,
            wet_dry=wet_dry,
            param1=p1,
            param2=p2
        )
        print(f"Set effect {i}: {result}")

    # Get final status
    status = controller.get_mixer_state(deck_id)
    print("\nFinal effects status:", status["effects"])

async def test_mixer_controls(controller: MixerController):
    """Test mixer controls"""
    print("\n=== Testing Mixer Controls ===")

    # Test crossfader
    print("\nTesting crossfader...")
    for pos in [-1.0, 0.0, 1.0, 0.0]:
        result = await controller.set_crossfader(pos)
        print(f"Set crossfader to {pos}: {result}")

    # Test master volume
    print("\nTesting master volume...")
    for vol in [0.5, 0.7, 0.9, 0.8]:
        result = await controller.set_master_volume(vol)
        print(f"Set master volume to {vol}: {result}")

    # Test headphone volume
    print("\nTesting headphone volume...")
    for vol in [0.5, 0.7, 0.9, 0.8]:
        result = await controller.set_headphone_volume(vol)
        print(f"Set headphone volume to {vol}: {result}")

    # Test headphone mix
    print("\nTesting headphone mix...")
    for mix in [0.0, 0.3, 0.7, 0.5]:
        result = await controller.set_headphone_mix(mix)
        print(f"Set headphone mix to {mix}: {result}")

async def main():
    """Main test function"""
    try:
        deck_id = 1  # Test with deck 1 by default

        print("=== VirtualDJ-MCP MixerController Tester ===")
        print("Make sure VirtualDJ is running.")

        # Create a test configuration
        config = VDJConfig(
            virtualdj_path="C:/Program Files/VirtualDJ/virtualdj.exe",
            rest_api_host="localhost",
            rest_api_port=8080,
            music_library_path=str(Path.home() / "Music"),
            max_decks=4
        )

        # Initialize the VirtualDJ client
        client = VirtualDJClient(config)

        # Initialize the mixer controller
        controller = MixerController(client)

        # Run tests
        await test_eq_controls(controller, deck_id)
        await test_effects(controller, deck_id)
        await test_mixer_controls(controller)

        print("\n=== All tests completed successfully! ===")

    except Exception as e:
        print(f"\nError during testing: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
