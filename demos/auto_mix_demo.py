"""
Auto Mix Demo - Automated DJ mixing demonstration

This script demonstrates VirtualDJ-MCP's ability to:
- Scan a music library for tracks
- Load tracks to decks automatically
- Perform crossfader mixing between decks
- Create a continuous DJ session

Run with: python auto_mix_demo.py [music_folder]
"""

import asyncio
import random
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from virtualdj_mcp.core.vdj_client import VirtualDJClient
from virtualdj_mcp.services.library_scanner import LibraryScanner
from virtualdj_mcp.config import VDJConfig


async def crossfade(vdj: VirtualDJClient, from_deck: int, to_deck: int, duration: float = 5.0):
    """Smoothly crossfade between two decks."""
    steps = 20
    step_delay = duration / steps
    
    # Calculate crossfader positions (-100 = deck 1, +100 = deck 2)
    start_pos = -100 if from_deck == 1 else 100
    end_pos = 100 if to_deck == 2 else -100
    
    for i in range(steps + 1):
        progress = i / steps
        position = start_pos + (end_pos - start_pos) * progress
        await vdj.set_crossfader(position)
        await asyncio.sleep(step_delay)
    
    print(f"   Crossfade complete: Deck {from_deck} -> Deck {to_deck}")


async def main():
    print("\n" + "=" * 60)
    print("🎵 VirtualDJ-MCP Auto Mix Demo")
    print("=" * 60)
    
    # Get music folder from args or use test fixtures
    if len(sys.argv) > 1:
        music_folder = Path(sys.argv[1])
    else:
        music_folder = Path(__file__).parent.parent / "tests" / "fixtures" / "audio"
    
    if not music_folder.exists():
        print(f"❌ Music folder not found: {music_folder}")
        print("   Usage: python auto_mix_demo.py [music_folder]")
        return
    
    print(f"📁 Music folder: {music_folder}")
    
    # Scan for tracks
    scanner = LibraryScanner()
    tracks = list(music_folder.glob("*.mp3")) + list(music_folder.glob("*.wav"))
    
    if len(tracks) < 2:
        print(f"❌ Need at least 2 tracks, found {len(tracks)}")
        return
    
    print(f"🎵 Found {len(tracks)} tracks:")
    for t in tracks[:5]:
        print(f"   - {t.name}")
    if len(tracks) > 5:
        print(f"   ... and {len(tracks) - 5} more")
    
    # Initialize VirtualDJ client
    config = VDJConfig()
    
    async with VirtualDJClient(config) as vdj:
        print("\n✅ Connected to VirtualDJ")
        
        # Check if VirtualDJ is running
        if not await vdj.is_running():
            print("⚠️  VirtualDJ not running - attempting to start...")
            if not await vdj.start_virtualdj():
                print("❌ Could not start VirtualDJ. Please start it manually.")
                return
            await asyncio.sleep(3)  # Wait for startup
        
        print("\n" + "-" * 40)
        print("🚀 Starting Auto Mix Demo")
        print("-" * 40)
        
        # Shuffle tracks for variety
        random.shuffle(tracks)
        
        # Load first track to deck 1
        track1 = tracks[0]
        print(f"\n▶ Loading to Deck 1: {track1.name}")
        await vdj.load_track(1, str(track1))
        await asyncio.sleep(1)
        
        # Load second track to deck 2
        track2 = tracks[1] if len(tracks) > 1 else tracks[0]
        print(f"▶ Loading to Deck 2: {track2.name}")
        await vdj.load_track(2, str(track2))
        await asyncio.sleep(1)
        
        # Set volumes
        await vdj.set_volume(1, 80)
        await vdj.set_volume(2, 80)
        
        # Start deck 1
        print("\n🎵 Playing Deck 1...")
        await vdj.set_crossfader(-100)  # Full left (deck 1)
        await vdj.play(1)
        
        # Let it play for a bit
        print("   Playing for 10 seconds...")
        await asyncio.sleep(10)
        
        # Cue up deck 2
        print("\n🎵 Cueing Deck 2...")
        await vdj.play(2)
        
        # Crossfade to deck 2
        print("🔀 Crossfading to Deck 2...")
        await crossfade(vdj, 1, 2, duration=5.0)
        
        # Stop deck 1
        await vdj.stop(1)
        
        # Let deck 2 play
        print("\n🎵 Deck 2 playing...")
        await asyncio.sleep(10)
        
        # Load next track to deck 1 while deck 2 plays
        if len(tracks) > 2:
            track3 = tracks[2]
            print(f"\n▶ Loading next track to Deck 1: {track3.name}")
            await vdj.load_track(1, str(track3))
            await asyncio.sleep(1)
            
            # Cue and crossfade back
            print("🎵 Cueing Deck 1...")
            await vdj.play(1)
            
            print("🔀 Crossfading to Deck 1...")
            await crossfade(vdj, 2, 1, duration=5.0)
            
            await vdj.stop(2)
            
            print("\n🎵 Deck 1 playing...")
            await asyncio.sleep(5)
        
        # Stop everything
        print("\n" + "-" * 40)
        print("✅ Demo complete!")
        print("-" * 40)
        
        await vdj.stop(1)
        await vdj.stop(2)
        await vdj.set_crossfader(0)  # Center


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

