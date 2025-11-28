"""
Test script for VirtualDJ-MCP mixer controls

This script provides interactive testing of the mixer controls.
Run with: python -m tests.test_mixer_controls
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.virtualdj_mcp.app import (
    set_eq_band,
    reset_eq,
    set_effect,
    set_crossfader_position,
    set_master_volume,
    set_headphone_volume,
    get_mixer_status
)

async def test_eq_controls(deck_id: int = 1):
    """Test EQ controls for a deck"""
    print(f"\n=== Testing EQ Controls (Deck {deck_id}) ===")
    
    # Reset EQ first
    print("\nResetting EQ...")
    result = await reset_eq(deck_id)
    print(f"Reset EQ: {result}")
    
    # Test setting EQ bands
    print("\nSetting EQ bands...")
    for band in ["low", "mid", "high"]:
        result = await set_eq_band(deck_id, band, 6.0)  # Boost by 6dB
        print(f"Set {band} to +6dB: {result}")
    
    # Test killing EQ bands
    print("\nKilling EQ bands...")
    for band in ["low", "mid", "high"]:
        result = await set_eq_band(deck_id, band, 0, kill=True)
        print(f"Killed {band}: {result}")
    
    # Get final status
    status = await get_mixer_status(deck_id)
    print("\nFinal EQ status:", status["mixer"]["eq"])

async def test_effects(deck_id: int = 1):
    """Test effect controls for a deck"""
    print(f"\n=== Testing Effect Controls (Deck {deck_id}) ===")
    
    # Test setting different effects
    effects = [
        ("filter", 75.0, 0.5, 0.0),  # Filter with wet/dry 75%
        ("flanger", 50.0, 0.3, 0.7),  # Flanger with parameters
        ("echo", 60.0, 0.4, 0.0)      # Echo effect
    ]
    
    for i, (effect_type, wet_dry, p1, p2) in enumerate(effects):
        print(f"\nSetting {effect_type} effect...")
        result = await set_effect(
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
    status = await get_mixer_status(deck_id)
    print("\nFinal effects status:", status["mixer"]["effects"])

async def test_mixer_controls():
    """Test mixer controls"""
    print("\n=== Testing Mixer Controls ===")
    
    # Test crossfader
    print("\nTesting crossfader...")
    for pos in [-1.0, 0.0, 1.0, 0.0]:
        result = await set_crossfader_position(pos)
        print(f"Set crossfader to {pos}: {result}")
    
    # Test master volume
    print("\nTesting master volume...")
    for vol in [0.5, 0.7, 0.9, 0.8]:
        result = await set_master_volume(vol)
        print(f"Set master volume to {vol}: {result}")
    
    # Test headphone controls
    print("\nTesting headphone controls...")
    for vol, mix in [(0.5, 0.5), (0.7, 0.3), (0.6, 0.7)]:
        result = await set_headphone_volume(vol, mix)
        print(f"Set headphone volume={vol}, mix={mix}: {result}")

async def main():
    """Main test function"""
    try:
        deck_id = 1  # Test with deck 1 by default
        
        print("=== VirtualDJ-MCP Mixer Controls Tester ===")
        print("Make sure VirtualDJ is running and the MCP server is started.")
        
        # Run tests
        await test_eq_controls(deck_id)
        await test_effects(deck_id)
        await test_mixer_controls()
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"\nError during testing: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    asyncio.run(main())
