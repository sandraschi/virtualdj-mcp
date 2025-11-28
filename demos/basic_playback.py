"""
Basic Playback Example for VirtualDJ-MCP

This script demonstrates basic deck control using VirtualDJ CLI commands:
- Loading tracks to decks
- Playback control (play/pause/stop)
- Volume adjustment
- Crossfader usage
- Status monitoring
"""
import asyncio
import os
from pathlib import Path

# Add parent directory to path to import from virtualdj_mcp
import sys
sys.path.append(str(Path(__file__).parent.parent))

from virtualdj_mcp.core.vdj_client import VirtualDJClient
from virtualdj_mcp.config import VDJConfig

async def main():
    print("🎵 VirtualDJ-MCP Basic Playback Example")
    print("=" * 50)

    # Load configuration
    config = VDJConfig()
    print(f"Using VirtualDJ path: {config.virtualdj_path}")

    # Initialize the VirtualDJ client
    async with VirtualDJClient(config) as vdj:
        print("✅ Connected to VirtualDJ client")

        # Check if VirtualDJ is running
        if not await vdj.is_running():
            print("⚠️  VirtualDJ is not running. Starting it...")
            if not await vdj.start_virtualdj():
                print("❌ Failed to start VirtualDJ. Please start it manually.")
                return

        print("[headphones] VirtualDJ is running")

        # Example track paths - update these to your music library
        track1 = r"C:\Users\sandr\Music\track1.mp3"  # Update this path!
        track2 = r"C:\Users\sandr\Music\track2.mp3"  # Update this path!

        # Check if tracks exist
        if not os.path.exists(track1) or not os.path.exists(track2):
            print("❌ Please update the track paths in the script to point to valid audio files")
            print(f"Looking for: {track1}")
            print(f"And: {track2}")
            return

        # Load tracks to decks using CLI commands
        print(f"🎵 Loading {track1} to deck 1")
        result = await vdj.send_command(f"deck 1 load '{track1}'")
        print(f"Load result: {result}")

        print(f"🎵 Loading {track2} to deck 2")
        result = await vdj.send_command(f"deck 2 load '{track2}'")
        print(f"Load result: {result}")

        # Start playing both decks
        print("▶️  Starting playback on both decks")
        await vdj.send_command("deck 1 play")
        await vdj.send_command("deck 2 play")

        # Set initial volumes (0-100)
        print("[speaker] Setting volumes to 70%")
        await vdj.send_command("deck 1 volume 70%")
        await vdj.send_command("deck 2 volume 70%")

        # Demonstrate crossfader (using VDJScript for smooth transitions)
        print("[mixer]️  Moving crossfader to center")
        await vdj.send_command("crossfader 0%")
        await asyncio.sleep(2)

        print("[mixer]️  Crossfading to deck 1")
        await vdj.send_command("crossfader -100%")  # Full left (deck 1)
        await asyncio.sleep(2)

        print("[mixer]️  Crossfading to deck 2")
        await vdj.send_command("crossfader 100%")   # Full right (deck 2)
        await asyncio.sleep(2)

        # Get status information
        print("📊 Getting deck status...")
        try:
            status = await vdj.get_status()
            print(f"Status: {status}")
        except Exception as e:
            print(f"Status check failed: {e}")

        # Reset crossfader to center
        await vdj.send_command("crossfader 0%")
        await asyncio.sleep(1)

        # Stop both decks
        print("[stop]️  Stopping both decks")
        await vdj.send_command("deck 1 stop")
        await vdj.send_command("deck 2 stop")

        print("✅ Example completed successfully!")
        print("\n💡 Tips:")
        print("- Update the track paths at the top of this script")
        print("- VirtualDJ must be installed and accessible")
        print("- Commands are sent via CLI: virtualdj.exe -cmd 'command'")

if __name__ == "__main__":
    asyncio.run(main())
