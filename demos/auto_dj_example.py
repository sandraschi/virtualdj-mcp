"""
Auto-DJ Example for VirtualDJ-MCP

This script demonstrates automated DJ mixing using VirtualDJ's built-in Auto-DJ
features and VDJScript for intelligent transitions.
"""
import argparse
import asyncio
import random

# Add parent directory to path to import from virtualdj_mcp
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from virtualdj_mcp.config import VDJConfig
from virtualdj_mcp.core.vdj_client import VirtualDJClient


async def main():
    print("🤖 VirtualDJ-MCP Auto-DJ Example")
    print("=" * 50)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run VirtualDJ Auto-DJ')
    parser.add_argument('--duration', type=int, default=5,
                       help='Duration of the Auto-DJ session in minutes (default: 5)')
    parser.add_argument('--genre', type=str, default=None,
                       help='Filter tracks by genre (e.g., "House", "Techno")')
    parser.add_argument('--bpm', type=int, default=None,
                       help='Target BPM (Auto-DJ will select tracks with similar BPM)')
    parser.add_argument('--energy', type=str, choices=['low', 'medium', 'high'],
                       default='medium', help='Energy level of the mix')

    args = parser.parse_args()

    # Load configuration
    config = VDJConfig()
    print(f"Using VirtualDJ path: {config.virtualdj_path}")

    # Initialize VirtualDJ client
    async with VirtualDJClient(config) as vdj:
        print("✅ Connected to VirtualDJ client")

        # Check if VirtualDJ is running
        if not await vdj.is_running():
            print("⚠️  VirtualDJ is not running. Starting it...")
            if not await vdj.start_virtualdj():
                print("❌ Failed to start VirtualDJ. Please start it manually.")
                return

        print("[headphones] VirtualDJ is running - starting Auto-DJ session")

        # Example track paths - in a real implementation, you'd scan a music library
        example_tracks = [
            r"C:\Users\sandr\Music\track1.mp3",
            r"C:\Users\sandr\Music\track2.mp3",
            r"C:\Users\sandr\Music\track3.mp3",
        ]

        # Filter tracks (simplified - you'd use actual library scanning)
        available_tracks = [t for t in example_tracks if Path(t).exists()]

        if len(available_tracks) < 2:
            print("❌ Need at least 2 tracks for Auto-DJ. Please add tracks to the example_tracks list.")
            return

        print(f"[disc] Found {len(available_tracks)} tracks for Auto-DJ")

        # Configure Auto-DJ using VirtualDJ's built-in features
        print("[mixer]️  Configuring Auto-DJ...")

        # Enable auto-mix mode with crossfader
        await vdj.send_command("automix_enable")
        await vdj.send_command("automix_crossfader 1")  # Use crossfader for transitions
        await vdj.send_command("automix_fadetime 8s")   # 8 second fade time

        # Load initial tracks
        print("🎵 Loading initial tracks...")
        await vdj.send_command(f"deck 1 load '{available_tracks[0]}'")
        await vdj.send_command(f"deck 2 load '{available_tracks[1]}'")

        # Start playback
        print("▶️  Starting Auto-DJ playback...")
        await vdj.send_command("deck 1 play")
        await vdj.send_command("automix_skip")  # Trigger first transition

        # Monitor the session
        session_duration = args.duration * 60  # Convert to seconds
        elapsed = 0

        print(f"[music] Auto-DJ session started for {args.duration} minutes")
        print("Press Ctrl+C to stop early")

        try:
            while elapsed < session_duration:
                await asyncio.sleep(10)  # Check every 10 seconds
                elapsed += 10

                # Get current status using VDJScript
                try:
                    deck1_title = await vdj.get_variable("deck1_title")
                    deck2_title = await vdj.get_variable("deck2_title")
                    automix_remain = await vdj.get_variable("automix_remain")

                    print(f"🎵 Deck1: {deck1_title or 'Unknown'} | Deck2: {deck2_title or 'Unknown'} | Next transition: {automix_remain or 'Unknown'}s")

                except Exception as e:
                    print(f"Status check: {e}")

                # Simulate adding more tracks to the queue (in real implementation, use VirtualDJ's playlist)
                if elapsed % 60 == 0:  # Every minute
                    if len(available_tracks) > 2:
                        next_track = random.choice(available_tracks[2:])
                        print(f"[disc] Adding track to queue: {Path(next_track).name}")

        except KeyboardInterrupt:
            print("\n[stop]️  Auto-DJ session interrupted by user")

        # Clean up
        print("[clean] Cleaning up Auto-DJ session...")
        await vdj.send_command("automix_disable")
        await vdj.send_command("deck 1 stop")
        await vdj.send_command("deck 2 stop")

        print("✅ Auto-DJ session completed!")
        print("\n💡 Tips:")
        print("- VirtualDJ's built-in Auto-DJ features are very powerful")
        print("- This example uses VirtualDJ's automix commands")
        print("- For advanced features, explore VirtualDJ's VDJScript capabilities")
        print("- Real Auto-DJ would scan your music library and match BPM/energy")

if __name__ == "__main__":
    asyncio.run(main())
