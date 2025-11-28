"""
Recording Example for VirtualDJ-MCP

This script demonstrates how to record your DJ mix using VirtualDJ's built-in recording features.
"""
import asyncio
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from virtualdj_mcp
import sys
sys.path.append(str(Path(__file__).parent.parent))

from virtualdj_mcp.core.vdj_client import VirtualDJClient
from virtualdj_mcp.config import VDJConfig

async def main():
    print("🎙️  VirtualDJ-MCP Recording Example")
    print("=" * 50)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Record a DJ mix with VirtualDJ')
    parser.add_argument('--name', type=str, default=None,
                      help='Name for the recording (default: auto-generated)')
    parser.add_argument('--format', type=str, default='mp3',
                      choices=['wav', 'mp3', 'ogg', 'flac'],
                      help='Output format for the recording')
    parser.add_argument('--duration', type=int, default=30,
                      help='Duration of the recording in seconds (default: 30)')

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

        print("🎧 VirtualDJ is running")

        # Generate recording name if not provided
        if not args.name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.name = f"vdj_mix_{timestamp}"

        print(f"🎵 Starting recording: {args.name}.{args.format}")
        print(f"⏱️  Duration: {args.duration} seconds")

        # Configure recording format and filename
        await vdj.send_command(f"rec_format {args.format}")
        await vdj.send_command(f"rec_filename '{args.name}'")

        # Start recording
        print("🔴 RECORDING STARTED")
        await vdj.send_command("rec")

        # Wait for the specified duration
        await asyncio.sleep(args.duration)

        # Stop recording
        print("⏹️  RECORDING STOPPED")
        await vdj.send_command("rec_stop")

        # Get recording status
        try:
            rec_time = await vdj.get_variable("rec_time")
            print(f"📊 Recording completed: {rec_time or 'Unknown'} seconds recorded")
        except Exception as e:
            print(f"Recording status: {e}")

        print("✅ Recording session completed!")
        print(f"💾 Check your VirtualDJ recordings folder for: {args.name}.{args.format}")
        print("\n💡 Tips:")
        print("- VirtualDJ saves recordings to its default recording directory")
        print("- Use 'rec' to start, 'rec_stop' to stop recording")
        print("- Configure format with 'rec_format' and filename with 'rec_filename'")
        print("- Check recording status with get_var 'rec'")

if __name__ == "__main__":
    asyncio.run(main())
